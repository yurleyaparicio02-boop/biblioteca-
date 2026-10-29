from typing import Annotated

from fastapi import APIRouter, Query, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencies import (
    Pagina,
    PaginacionDep,
    requiere_rol,
)
from ..models.usuario import RolUsuario, Usuario
from ..schemas.prestamos import (
    EstadoPrestamo,
    MisMultasRespuesta,
    PrestamoResponse,
)
from ..schemas.socios import (
    SocioActualizar,
    SocioActualizarPropio,
    SocioCrear,
    SocioResponse,
)

RESPUESTAS_ERROR = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Socio no encontrado"},
}

router = APIRouter(
    prefix="/socios",
    tags=["Socios"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "",
    response_model=Pagina[SocioResponse],
    summary="Listar socios con paginación",
)
def listar_socios(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
    activo: bool | None = None,
):
    return controllers.socios.listar_socios(db, paginacion, activo)


@router.get(
    "/me",
    response_model=SocioResponse,
    summary="Obtener perfil del socio autenticado",
)
def obtener_mi_perfil(
    db: SessionDep,
    usuario: Usuario = requiere_rol(RolUsuario.socio),
):
    return controllers.socios.obtener_mi_perfil(db, usuario)


@router.patch(
    "/me",
    response_model=SocioResponse,
    summary="Actualizar nombre y teléfono del socio autenticado",
)
def actualizar_mi_perfil(
    datos: SocioActualizarPropio,
    db: SessionDep,
    usuario: Usuario = requiere_rol(RolUsuario.socio),
):
    return controllers.socios.actualizar_mi_perfil(db, usuario, datos)


@router.get(
    "/me/prestamos",
    response_model=Pagina[PrestamoResponse],
    summary="Listar préstamos del socio autenticado",
)
def listar_mis_prestamos(
    db: SessionDep,
    paginacion: PaginacionDep,
    usuario: Usuario = requiere_rol(RolUsuario.socio),
    estado: Annotated[EstadoPrestamo | None, Query()] = None,
):
    return controllers.socios.listar_mis_prestamos(
        db, usuario, paginacion, estado
    )


@router.get(
    "/me/multas",
    response_model=MisMultasRespuesta,
    summary="Listar multas pendientes y total adeudado del socio autenticado",
)
def listar_mis_multas(
    db: SessionDep,
    usuario: Usuario = requiere_rol(RolUsuario.socio),
):
    return controllers.socios.listar_mis_multas(db, usuario)


@router.get(
    "/{socio_id}",
    response_model=SocioResponse,
    summary="Obtener socio por ID",
)
def obtener_socio(
    socio_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.socios.obtener_socio(db, socio_id)


@router.get(
    "/{socio_id}/prestamos",
    response_model=Pagina[PrestamoResponse],
    summary="Listar préstamos de un socio por ID",
)
def listar_prestamos_socio(
    socio_id: int,
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
    estado: Annotated[EstadoPrestamo | None, Query()] = None,
):
    return controllers.socios.listar_prestamos_socio(
        db, socio_id, paginacion, estado
    )


@router.post(
    "",
    response_model=SocioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un socio",
)
def crear_socio(
    datos: SocioCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.socios.crear_socio(db, datos)


@router.patch(
    "/{socio_id}",
    response_model=SocioResponse,
    summary="Actualizar un socio por ID",
)
def actualizar_socio(
    socio_id: int,
    datos: SocioActualizar,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.socios.actualizar_socio(db, socio_id, datos)


@router.delete(
    "/{socio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un socio",
)
def eliminar_socio(
    socio_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin),
) -> None:
    controllers.socios.eliminar_socio(db, socio_id)
