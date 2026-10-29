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
    DevolucionCrear,
    EstadoPrestamo,
    PrestamoCrear,
    PrestamoDetalle,
    PrestamoResponse,
)

RESPUESTAS_ERROR = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "Préstamo no encontrado"},
}

router = APIRouter(
    prefix="/prestamos",
    tags=["Préstamos"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "",
    response_model=Pagina[PrestamoResponse],
    summary="Listar préstamos con filtros y paginación",
)
@router.get(
    "/",
    response_model=Pagina[PrestamoResponse],
    include_in_schema=False,
)
def listar_prestamos(
    db: SessionDep,
    paginacion: PaginacionDep,
    usuario: Usuario = requiere_rol(
        RolUsuario.socio, RolUsuario.bibliotecario, RolUsuario.admin
    ),
    estado: Annotated[EstadoPrestamo | None, Query()] = None,
    socio_id: Annotated[int | None, Query(gt=0)] = None,
    libro_id: Annotated[int | None, Query(gt=0)] = None,
):
    return controllers.prestamos.listar_prestamos(
        db, paginacion, estado, socio_id, libro_id, usuario
    )


@router.get(
    "/{prestamo_id}",
    response_model=PrestamoDetalle,
    summary="Obtener detalle de un préstamo por ID",
)
def obtener_prestamo(
    prestamo_id: int,
    db: SessionDep,
    usuario: Usuario = requiere_rol(
        RolUsuario.socio, RolUsuario.bibliotecario, RolUsuario.admin
    ),
):
    return controllers.prestamos.obtener_prestamo(db, prestamo_id, usuario)


@router.post(
    "",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo préstamo",
)
@router.post(
    "/",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def registrar_prestamo(
    datos: PrestamoCrear,
    db: SessionDep,
    usuario: Usuario = requiere_rol(
        RolUsuario.admin, RolUsuario.bibliotecario
    ),
):
    return controllers.prestamos.registrar_prestamo(db, datos, usuario.id)


@router.post(
    "/{prestamo_id}/devolucion",
    response_model=PrestamoResponse,
    summary="Registrar la devolución de un préstamo",
)
def registrar_devolucion(
    prestamo_id: int,
    datos: DevolucionCrear,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.prestamos.registrar_devolucion(db, prestamo_id, datos)


@router.post(
    "/{prestamo_id}/pago-multa",
    response_model=PrestamoResponse,
    summary="Registrar el pago de la multa de un préstamo",
)
@router.post(
    "/{prestamo_id}/multa/pago",
    response_model=PrestamoResponse,
    include_in_schema=False,
)
def pagar_multa(
    prestamo_id: int,
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    """Marca como pagada la multa de un préstamo ya devuelto."""
    return controllers.prestamos.pagar_multa(db, prestamo_id)
