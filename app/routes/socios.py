from typing import Annotated

from fastapi import APIRouter, Query, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import PaginacionDep, Pagina
from ..schemas.prestamos import EstadoPrestamo, PrestamoResponse
from ..schemas.socios import SocioActualizar, SocioCrear, SocioResponse

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=Pagina[SocioResponse])
def listar_socios(
    db: SessionDep,
    paginacion: PaginacionDep,
    activo: bool | None = None,
):
    return controllers.socios.listar_socios(db, paginacion, activo)


@router.get("/{socio_id}", response_model=SocioResponse)
def obtener_socio(socio_id: int, db: SessionDep):
    return controllers.socios.obtener_socio(db, socio_id)


@router.get("/{socio_id}/prestamos", response_model=Pagina[PrestamoResponse])
def listar_prestamos_socio(
    socio_id: int,
    db: SessionDep,
    paginacion: PaginacionDep,
    estado: Annotated[EstadoPrestamo | None, Query()] = None,
):
    return controllers.socios.listar_prestamos_socio(
        db, socio_id, paginacion, estado
    )


@router.post("", response_model=SocioResponse, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCrear, db: SessionDep):
    return controllers.socios.crear_socio(db, datos)


@router.patch("/{socio_id}", response_model=SocioResponse)
def actualizar_socio(
    socio_id: int, datos: SocioActualizar, db: SessionDep
):
    return controllers.socios.actualizar_socio(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, db: SessionDep) -> None:
    controllers.socios.eliminar_socio(db, socio_id)
