from typing import Annotated

from fastapi import APIRouter, Depends, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencies import (
    Pagina,
    PaginacionDep,
    requiere_rol,
)
from ..models.usuario import RolUsuario, Usuario
from ..schemas.libros import (
    FiltroLibros,
    LibroActualizar,
    LibroCrear,
    LibroResponse,
)

RESPUESTAS_ERROR = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Libro no encontrado"},
}

router = APIRouter(
    prefix="/libros",
    tags=["Libros"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "",
    response_model=Pagina[LibroResponse],
    summary="Listar libros del catálogo con filtros y paginación",
)
def listar_libros(
    db: SessionDep,
    paginacion: PaginacionDep,
    filtros: Annotated[FiltroLibros, Depends()],
):
    return controllers.libros.listar_libros(db, paginacion, filtros)


@router.get(
    "/{libro_id}",
    response_model=LibroResponse,
    summary="Obtener detalle de un libro por ID",
)
def obtener_libro(libro_id: int, db: SessionDep):
    return controllers.libros.obtener_libro(db, libro_id)


@router.post(
    "",
    response_model=LibroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo libro",
)
def crear_libro(
    datos: LibroCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.libros.crear_libro(db, datos)


@router.patch(
    "/{libro_id}",
    response_model=LibroResponse,
    summary="Actualizar un libro existente",
)
def actualizar_libro(
    libro_id: int,
    datos: LibroActualizar,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.libros.actualizar_libro(db, libro_id, datos)


@router.delete(
    "/{libro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un libro",
)
def eliminar_libro(
    libro_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
) -> None:
    controllers.libros.eliminar_libro(db, libro_id)
