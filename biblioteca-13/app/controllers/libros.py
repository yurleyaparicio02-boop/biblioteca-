from sqlalchemy import delete, exists, func, select
from sqlalchemy.orm import Session, selectinload

from ..core.config import get_settings
from ..core.dependencies import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..core.texto import patron_busqueda
from ..models import Autor, Categoria, Libro, Prestamo, libro_categoria
from ..schemas.libros import (
    FiltroLibros,
    ImagenLibroResponse,
    LibroActualizar,
    LibroCrear,
)
from ..utils.subir_imagen import subir_bytes_cloudinary


def _prestamos_abiertos_por_libro():
    return (
        select(Prestamo.libro_id, func.count(Prestamo.id).label("abiertos"))
        .where(Prestamo.fecha_devolucion.is_(None))
        .group_by(Prestamo.libro_id)
        .subquery()
    )


IMAGENES_PREDETERMINADAS_LIBROS: dict[str, str] = {
    "9780307474728": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/cien_a%C3%B1os_de_soledad_lnad7d.jpg",
    "cien anios de soledad": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/cien_a%C3%B1os_de_soledad_lnad7d.jpg",
    "cien años de soledad": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/cien_a%C3%B1os_de_soledad_lnad7d.jpg",
    "9788401352836": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/images_s13exd.jpg",
    "la casa de los espiritus": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/images_s13exd.jpg",
    "la casa de los espíritus": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/images_s13exd.jpg",
    "9780307387264": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/26748ccf3fddb99a7d3d14d8db88ca57_hnyyrr.jpg",
    "el amor en los tiempos del colera": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/26748ccf3fddb99a7d3d14d8db88ca57_hnyyrr.jpg",
    "el amor en los tiempos del cólera": "https://res.cloudinary.com/v1cv0zdo/image/upload/f_auto/q_auto/26748ccf3fddb99a7d3d14d8db88ca57_hnyyrr.jpg",
}


def _imagen_por_defecto(isbn: str, titulo: str) -> str | None:
    return (
        IMAGENES_PREDETERMINADAS_LIBROS.get(isbn)
        or IMAGENES_PREDETERMINADAS_LIBROS.get(titulo.strip().lower())
    )


def _resolver_imagen_libro(libro: Libro) -> str | None:
    if libro.imagen_url and "res.cloudinary.com/demo/" not in libro.imagen_url:
        return libro.imagen_url
    return _imagen_por_defecto(libro.isbn, libro.titulo)


def _libro_response(libro: Libro, abiertos: int) -> dict[str, object]:
    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "isbn": libro.isbn,
        "anio_publicacion": libro.anio_publicacion,
        "ejemplares": libro.ejemplares,
        "imagen_url": _resolver_imagen_libro(libro),
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
    if not valores.get("imagen_url"):
        valores["imagen_url"] = _imagen_por_defecto(datos.isbn, datos.titulo)
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


def asignar_imagen_libro(
    db: Session,
    libro_id: int,
    archivo_bytes: bytes,
    content_type: str | None,
) -> ImagenLibroResponse:
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")

    secure_url, public_id = subir_bytes_cloudinary(archivo_bytes, content_type)
    libro.imagen_url = secure_url
    db.commit()
    db.refresh(libro)

    return ImagenLibroResponse(
        libro_id=libro.id,
        imagen_url=secure_url,
        public_id=public_id,
    )
