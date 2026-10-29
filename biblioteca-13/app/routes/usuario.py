from typing import Annotated

from fastapi import APIRouter, Query, status

from app.controllers import usuario as usuario_controller
from app.core.dependencies import (
    Pagina,
    PaginacionDep,
    SessionDep,
    requiere_rol,
)
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import (
    UsuarioCambiarActivo,
    UsuarioCambiarRol,
    UsuarioCrear,
    UsuarioRespuesta,
)

RESPUESTAS_ERROR = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Usuario no encontrado"},
}

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "",
    response_model=Pagina[UsuarioRespuesta],
    summary="Listar usuarios con paginación y filtros",
)
def listar_usuarios(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
    rol: Annotated[RolUsuario | None, Query()] = None,
    activo: Annotated[bool | None, Query()] = None,
):
    return usuario_controller.listar_usuarios(db, paginacion, rol, activo)


@router.post(
    "",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario con rol bibliotecario o admin",
)
def crear_usuario(
    datos: UsuarioCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
):
    return usuario_controller.crear_usuario(db, datos)


@router.patch(
    "/{usuario_id}/rol",
    response_model=UsuarioRespuesta,
    summary="Cambiar el rol de un usuario",
)
def cambiar_rol(
    usuario_id: int,
    datos: UsuarioCambiarRol,
    db: SessionDep,
    admin_actual: Usuario = requiere_rol(RolUsuario.admin),
):
    return usuario_controller.cambiar_rol_usuario(
        db, usuario_id, datos, admin_actual
    )


@router.patch(
    "/{usuario_id}/activo",
    response_model=UsuarioRespuesta,
    summary="Activar o desactivar un usuario",
)
def cambiar_activo(
    usuario_id: int,
    datos: UsuarioCambiarActivo,
    db: SessionDep,
    admin_actual: Usuario = requiere_rol(RolUsuario.admin),
):
    return usuario_controller.cambiar_activo_usuario(
        db, usuario_id, datos, admin_actual
    )
