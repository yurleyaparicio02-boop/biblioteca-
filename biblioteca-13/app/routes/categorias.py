from typing import Any

from fastapi import APIRouter, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencies import (
    Pagina,
    PaginacionDep,
    requiere_rol,
)
from ..models.usuario import RolUsuario, Usuario
from ..schemas.categorias import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaResponse,
)

RESPUESTAS_ERROR: dict[int | str, dict[str, Any]] = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Categoría no encontrada"},
}

RESPUESTAS_AUTENTICACION: dict[int | str, dict[str, Any]] = {
    clave: valor for clave, valor in RESPUESTAS_ERROR.items() if clave != 404
}

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
)


@router.get(
    "",
    response_model=Pagina[CategoriaResponse],
    summary="Listar categorías con paginación",
    responses=RESPUESTAS_AUTENTICACION,
)
def listar_categorias(db: SessionDep, paginacion: PaginacionDep):
    return controllers.categorias.listar_categorias(db, paginacion)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Obtener una categoría por ID",
    responses=RESPUESTAS_ERROR,
)
def obtener_categoria(categoria_id: int, db: SessionDep):
    return controllers.categorias.obtener_categoria(db, categoria_id)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría",
    responses=RESPUESTAS_AUTENTICACION,
)
def crear_categoria(
    datos: CategoriaCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.categorias.crear_categoria(db, datos)


@router.patch(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Actualizar una categoría",
    responses=RESPUESTAS_ERROR,
)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaActualizar,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.categorias.actualizar_categoria(db, categoria_id, datos)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
    responses=RESPUESTAS_ERROR,
)
def eliminar_categoria(
    categoria_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
) -> None:
    controllers.categorias.eliminar_categoria(db, categoria_id)
