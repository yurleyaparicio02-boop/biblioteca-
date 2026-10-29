from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencies import (
    Pagina,
    PaginacionDep,
    requiere_rol,
)
from ..models.usuario import RolUsuario, Usuario
from ..schemas.autores import AutorActualizar, AutorCrear, AutorResponse
from ..schemas.libros import LibroResponse

RESPUESTAS_ERROR: dict[int | str, dict[str, Any]] = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Autor no encontrado"},
}

router = APIRouter(
    prefix="/autores",
    tags=["Autores"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "",
    response_model=Pagina[AutorResponse],
    summary="Listar autores con paginación",
)
def listar_autores(
    db: SessionDep,
    paginacion: PaginacionDep,
    nacionalidad: Annotated[str | None, Query(max_length=60)] = None,
):
    return controllers.autores.listar_autores(db, paginacion, nacionalidad)


@router.get(
    "/{autor_id}",
    response_model=AutorResponse,
    summary="Obtener un autor por ID",
)
def obtener_autor(autor_id: int, db: SessionDep):
    return controllers.autores.obtener_autor(db, autor_id)


@router.get(
    "/{autor_id}/libros",
    response_model=Pagina[LibroResponse],
    summary="Listar libros de un autor",
)
def listar_libros_autor(
    autor_id: int, db: SessionDep, paginacion: PaginacionDep
):
    return controllers.autores.listar_libros_autor(db, autor_id, paginacion)


@router.post(
    "",
    response_model=AutorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un autor",
)
def crear_autor(
    datos: AutorCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.autores.crear_autor(db, datos)


@router.patch(
    "/{autor_id}",
    response_model=AutorResponse,
    summary="Actualizar un autor",
)
def actualizar_autor(
    autor_id: int,
    datos: AutorActualizar,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.autores.actualizar_autor(db, autor_id, datos)


@router.delete(
    "/{autor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un autor",
)
def eliminar_autor(
    autor_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
) -> None:
    controllers.autores.eliminar_autor(db, autor_id)
