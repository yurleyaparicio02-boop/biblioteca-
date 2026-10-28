from typing import Annotated

from fastapi import APIRouter, Query, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import Pagina, PaginacionDep
from ..schemas.prestamos import (
    DevolucionCrear,
    EstadoPrestamo,
    PrestamoCrear,
    PrestamoDetalle,
    PrestamoResponse,
)

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.get("/", response_model=Pagina[PrestamoResponse])
@router.get("", response_model=Pagina[PrestamoResponse], include_in_schema=False)
def listar_prestamos(
    db: SessionDep,
    paginacion: PaginacionDep,
    estado: Annotated[EstadoPrestamo | None, Query()] = None,
    socio_id: Annotated[int | None, Query(gt=0)] = None,
    libro_id: Annotated[int | None, Query(gt=0)] = None,
):
    return controllers.prestamos.listar_prestamos(
        db, paginacion, estado, socio_id, libro_id
    )


@router.get("/{prestamo_id}", response_model=PrestamoDetalle)
def obtener_prestamo(prestamo_id: int, db: SessionDep):
    return controllers.prestamos.obtener_prestamo(db, prestamo_id)


@router.post(
    "/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED
)
@router.post(
    "",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def registrar_prestamo(datos: PrestamoCrear, db: SessionDep):
    return controllers.prestamos.registrar_prestamo(db, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoResponse)
def registrar_devolucion(
    prestamo_id: int, datos: DevolucionCrear, db: SessionDep
):
    return controllers.prestamos.registrar_devolucion(db, prestamo_id, datos)

@router.post("/{prestamo_id}/pago-multa", response_model=PrestamoResponse)
@router.post(
    "/{prestamo_id}/multa/pago",
    response_model=PrestamoResponse,
    include_in_schema=False,
)
def pagar_multa(prestamo_id: int, db: SessionDep):
    """Marca como pagada la multa de un préstamo ya devuelto."""
    return controllers.prestamos.pagar_multa(db, prestamo_id)