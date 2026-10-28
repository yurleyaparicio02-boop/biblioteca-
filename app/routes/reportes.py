from typing import Annotated

from fastapi import APIRouter, Query

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import PaginacionDep, Pagina
from ..schemas.reportes import (
    LibrosPorCategoria,
    LibroMasPrestado,
    PrestamoVencidoReporte,
    ReporteAutor,
    ResumenBiblioteca,
    SocioMultas,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/libros-mas-prestados", response_model=Pagina[LibroMasPrestado])
def reporte_libros_mas_prestados(
    db: SessionDep,
    limite: Annotated[int, Query(ge=1, le=100)] = 5,
    skip: Annotated[int, Query(ge=0)] = 0,
):
    return controllers.reportes.libros_mas_prestados(db, limite, skip)


@router.get("/categorias", response_model=Pagina[LibrosPorCategoria])
def reporte_categorias(db: SessionDep, paginacion: PaginacionDep):
    return controllers.reportes.categorias_con_libros(db, paginacion)


@router.get("/prestamos-vencidos", response_model=Pagina[PrestamoVencidoReporte])
def reporte_prestamos_vencidos(db: SessionDep, paginacion: PaginacionDep):
    return controllers.reportes.prestamos_vencidos(db, paginacion)


@router.get("/socios-con-multas", response_model=Pagina[SocioMultas])
def reporte_socios_con_multas(
    db: SessionDep,
    paginacion: PaginacionDep,
    solo_pendientes: bool = True,
):
    return controllers.reportes.socios_con_multas(db, paginacion, solo_pendientes)


@router.get("/autores", response_model=Pagina[ReporteAutor])
def reporte_autores(db: SessionDep, paginacion: PaginacionDep):
    return controllers.reportes.reporte_autores(db, paginacion)


@router.get("/resumen", response_model=ResumenBiblioteca)
def reporte_resumen(db: SessionDep):
    return controllers.reportes.resumen_biblioteca(db)
