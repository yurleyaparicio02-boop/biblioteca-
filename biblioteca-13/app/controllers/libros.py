from sqlalchemy import delete, exists, func, select
from sqlalchemy.orm import Session, selectinload

from ..core.dependencies import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..core.texto import patron_busqueda
from ..models import Autor, Categoria, Libro, Prestamo, libro_categoria
from ..schemas.libros import FiltroLibros, LibroActualizar, LibroCrear


def _prestamos_abiertos_por_libro():
    return (
        select(Prestamo.libro_id, func.count(Prestamo.id).label("abiertos"))
        .where(Prestamo.fecha_devolucion.is_(None))
        .group_by(Prestamo.libro_id)
        .subquery()
    )


def _libro_response(libro: Libro, abiertos: int) -> dict[str, object]:
    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "isbn": libro.isbn,
        "anio_publicacion": libro.anio_publicacion,
        "ejemplares": libro.ejemplares,
        "disponibles": libro.ejemplares - abiertos,
        "autor": libro.autor,
        "categorias": libro.categorias,
    }


def _consulta_libros():
    abiertos = _prestamos_abiertos_por_libro()
    return (
        select(Libro, func.coalesce(abiertos.c.abiertos, 0))
        .outerjoin(abiertos, abiertos.c.libro_id == Libro.id)
        .options(selectinload(Libro.autor), selectinload(Libro.categorias))
    )


def listar_libros(
    db: Session, paginacion: Paginacion, filtros: FiltroLibros
) -> Pagina[dict[str, object]]:
    consulta = _consulta_libros()
    patron_titulo = patron_busqueda(filtros.buscar)
    if patron_titulo:
        consulta = consulta.where(Libro.titulo.ilike(patron_titulo, escape="\\"))

    patron_autor = patron_busqueda(filtros.autor)
    if patron_autor:
        consulta = consulta.where(
            exists(
                select(Autor.id).where(
                    Autor.id == Libro.autor_id,
                    Autor.nombre.ilike(patron_autor, escape="\\"),
                )
            )
        )
    if filtros.categoria_id:
        consulta = consulta.where(
            exists(
                select(libro_categoria.c.libro_id).where(
                    libro_categoria.c.libro_id == Libro.id,
                    libro_categoria.c.categoria_id == filtros.categoria_id,
                )
            )
        )
    if filtros.desde is not None:
        consulta = consulta.where(Libro.anio_publicacion >= filtros.desde)
    if filtros.hasta is not None:
        consulta = consulta.where(Libro.anio_publicacion <= filtros.hasta)
    if filtros.orden.value == "anio":
        consulta = consulta.order_by(Libro.anio_publicacion, Libro.id)
    elif filtros.orden.value == "-anio":
        consulta = consulta.order_by(Libro.anio_publicacion.desc(), Libro.id)
    else:
        consulta = consulta.order_by(Libro.titulo, Libro.id)
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = db.execute(
        consulta.offset(paginacion.skip).limit(paginacion.limit)
    ).all()
    items = [_libro_response(libro, abiertos) for libro, abiertos in filas]
    return armar_pagina(items, total, paginacion)


def obtener_libro(db: Session, libro_id: int) -> dict[str, object]:
    fila = db.execute(_consulta_libros().where(Libro.id == libro_id)).first()
    if fila is None:
        raise NoEncontrado("Libro no encontrado")
    libro, abiertos = fila
    return _libro_response(libro, abiertos)


def crear_libro(db: Session, datos: LibroCrear) -> dict[str, object]:
    if db.get(Autor, datos.autor_id) is None:
        raise NoEncontrado("El autor especificado no existe")
    categorias = list(
        db.scalars(
            select(Categoria).where(Categoria.id.in_(datos.categoria_ids))
        ).all()
    )
    if len(categorias) != len(datos.categoria_ids):
        raise NoEncontrado("Una o más categorías no existen")
    if db.scalar(select(Libro.id).where(Libro.isbn == datos.isbn)):
        raise Conflicto("Ya existe un libro con ese ISBN")
    valores = datos.model_dump(exclude={"categoria_ids"})
    libro = Libro(**valores, categorias=categorias)
    db.add(libro)
    db.commit()
    db.refresh(libro)
    return obtener_libro(db, libro.id)


def actualizar_libro(
    db: Session, libro_id: int, datos: LibroActualizar
) -> dict[str, object]:
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    cambios = datos.model_dump(exclude_unset=True)
    categoria_ids = cambios.pop("categoria_ids", None)
    if cambios.get("autor_id") is not None and db.get(Autor, cambios["autor_id"]) is None:
        raise NoEncontrado("El autor especificado no existe")
    if categoria_ids is not None:
        categorias = list(
            db.scalars(select(Categoria).where(Categoria.id.in_(categoria_ids))).all()
        )
        if len(categorias) != len(categoria_ids):
            raise NoEncontrado("Una o más categorías no existen")
        libro.categorias = categorias
    if "isbn" in cambios and cambios["isbn"] != libro.isbn:
        if db.scalar(
            select(Libro.id).where(
                Libro.isbn == cambios["isbn"], Libro.id != libro_id
            )
        ):
            raise Conflicto("El ISBN ya está asignado a otro libro")
    abiertos = (
        db.scalar(
            select(func.count(Prestamo.id)).where(
                Prestamo.libro_id == libro_id,
                Prestamo.fecha_devolucion.is_(None),
            )
        )
        or 0
    )
    ejemplares = cambios.get("ejemplares", libro.ejemplares)
    if ejemplares < abiertos:
        raise ReglaNegocio(
            "Los ejemplares no pueden ser menos que los préstamos sin devolver"
        )
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    db.commit()
    return obtener_libro(db, libro_id)


def eliminar_libro(db: Session, libro_id: int) -> None:
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    prestamos_abiertos = (
        db.scalar(
            select(func.count(Prestamo.id)).where(
                Prestamo.libro_id == libro_id,
                Prestamo.fecha_devolucion.is_(None),
            )
        )
        or 0
    )
    if prestamos_abiertos:
        raise Conflicto("No se puede eliminar el libro porque tiene préstamos sin devolver")
    db.execute(delete(Prestamo).where(Prestamo.libro_id == libro_id))
    db.delete(libro)
    db.commit()
