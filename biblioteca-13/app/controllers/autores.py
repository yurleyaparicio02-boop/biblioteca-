from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencias import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado
from ..core.texto import patron_busqueda
from ..models import Autor, Libro
from ..schemas.autores import AutorActualizar, AutorCrear, AutorResponse
from .libros import _consulta_libros, _libro_response


def listar_autores(
    db: Session, paginacion: Paginacion, nacionalidad: str | None = None
) -> Pagina[AutorResponse]:
    consulta = select(Autor)
    patron = patron_busqueda(nacionalidad)
    if patron:
        consulta = consulta.where(Autor.nacionalidad.ilike(patron, escape="\\"))
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    autores = list(
        db.scalars(
            consulta.order_by(Autor.id).offset(paginacion.skip).limit(paginacion.limit)
        ).all()
    )
    items = [AutorResponse.model_validate(autor) for autor in autores]
    return armar_pagina(items, total, paginacion)


def obtener_autor(db: Session, autor_id: int) -> Autor:
    autor = db.get(Autor, autor_id)
    if autor is None:
        raise NoEncontrado("Autor no encontrado")
    return autor


def crear_autor(db: Session, datos: AutorCrear) -> Autor:
    existente = db.scalar(
        select(Autor).where(func.lower(Autor.nombre) == datos.nombre.lower())
    )
    if existente:
        raise Conflicto("Ya existe un autor con ese nombre")
    autor = Autor(**datos.model_dump())
    db.add(autor)
    db.commit()
    db.refresh(autor)
    return autor


def actualizar_autor(db: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    autor = obtener_autor(db, autor_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "nombre" in cambios and cambios["nombre"] is not None:
        duplicado = db.scalar(
            select(Autor).where(
                Autor.id != autor_id,
                func.lower(Autor.nombre) == cambios["nombre"].lower(),
            )
        )
        if duplicado:
            raise Conflicto("Ya existe un autor con ese nombre")
    for campo, valor in cambios.items():
        setattr(autor, campo, valor)
    db.commit()
    db.refresh(autor)
    return autor


def eliminar_autor(db: Session, autor_id: int) -> None:
    autor = obtener_autor(db, autor_id)
    if db.scalar(select(Libro.id).where(Libro.autor_id == autor_id).limit(1)):
        raise Conflicto("No se puede eliminar el autor porque tiene libros")
    db.delete(autor)
    db.commit()


def listar_libros_autor(
    db: Session, autor_id: int, paginacion: Paginacion
) -> Pagina[dict[str, object]]:
    obtener_autor(db, autor_id)
    base = _consulta_libros().where(Libro.autor_id == autor_id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    consulta = (
        base.order_by(Libro.id).offset(paginacion.skip).limit(paginacion.limit)
    )
    items = [
        _libro_response(libro, abiertos)
        for libro, abiertos in db.execute(consulta).all()
    ]
    return armar_pagina(items, total, paginacion)
