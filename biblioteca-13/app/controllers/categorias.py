from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencies import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Categoria
from ..schemas.categorias import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaResponse,
)


def listar_categorias(
    db: Session, paginacion: Paginacion
) -> Pagina[CategoriaResponse]:
    consulta = select(Categoria)
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    categorias = list(
        db.scalars(
            consulta.order_by(Categoria.id)
            .offset(paginacion.skip)
            .limit(paginacion.limit)
        ).all()
    )
    items = [CategoriaResponse.model_validate(c) for c in categorias]
    return armar_pagina(items, total, paginacion)


def obtener_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NoEncontrado("Categoría no encontrada")
    return categoria


def crear_categoria(db: Session, datos: CategoriaCrear) -> Categoria:
    if db.scalar(select(Categoria.id).where(Categoria.nombre == datos.nombre)):
        raise Conflicto("Ya existe una categoría con ese nombre")
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def actualizar_categoria(
    db: Session, categoria_id: int, datos: CategoriaActualizar
) -> Categoria:
    categoria = obtener_categoria(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "nombre" in cambios and cambios["nombre"] is not None:
        duplicada = db.scalar(
            select(Categoria.id).where(
                Categoria.id != categoria_id, Categoria.nombre == cambios["nombre"]
            )
        )
        if duplicada:
            raise Conflicto("Ya existe una categoría con ese nombre")
    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def eliminar_categoria(db: Session, categoria_id: int) -> None:
    categoria = obtener_categoria(db, categoria_id)
    categoria.libros.clear()
    db.delete(categoria)
    db.commit()
