from typing import Annotated, Any

from fastapi import APIRouter, Query

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencies import (
    Pagina,
    PaginacionDep,
    requiere_rol,
)
from ..models.usuario import RolUsuario, Usuario
from ..schemas.reportes import (
    LibroMasPrestado,
    LibrosPorCategoria,
    PrestamoVencidoReporte,
    ReporteAutor,
    ResumenBiblioteca,
    SocioMultas,
)

RESPUESTAS_ERROR: dict[int | str, dict[str, Any]] = {
    401: {"description": "No autenticado"},
    403: {"description": "No tiene permisos para esta acción"},
    404: {"description": "No encontrado"},
}

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
    responses=RESPUESTAS_ERROR,
)


@router.get(
    "/libros-mas-prestados",
    response_model=Pagina[LibroMasPrestado],
    summary="Reporte de los libros más prestados",
)
def reporte_libros_mas_prestados(
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
    limite: Annotated[int, Query(ge=1, le=100)] = 5,
    skip: Annotated[int, Query(ge=0)] = 0,
):
    return controllers.reportes.libros_mas_prestados(db, limite, skip)


@router.get(
    "/categorias",
    response_model=Pagina[LibrosPorCategoria],
    summary="Reporte de cantidad de libros por categoría",
)
def reporte_categorias(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.reportes.categorias_con_libros(db, paginacion)


@router.get(
    "/prestamos-vencidos",
    response_model=Pagina[PrestamoVencidoReporte],
    summary="Reporte de préstamos vencidos sin devolver",
)
def reporte_prestamos_vencidos(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.reportes.prestamos_vencidos(db, paginacion)


@router.get(
    "/socios-con-multas",
    response_model=Pagina[SocioMultas],
    summary="Reporte de socios con multas",
)
def reporte_socios_con_multas(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
    solo_pendientes: bool = True,
):
    return controllers.reportes.socios_con_multas(
        db, paginacion, solo_pendientes
    )


@router.get(
    "/autores",
    response_model=Pagina[ReporteAutor],
    summary="Reporte estadístico por autor",
)
def reporte_autores(
    db: SessionDep,
    paginacion: PaginacionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.reportes.reporte_autores(db, paginacion)


@router.get(
    "/resumen",
    response_model=ResumenBiblioteca,
    summary="Resumen general del estado de la biblioteca",
)
def reporte_resumen(
    db: SessionDep,
    _: Usuario = requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario),
):
    return controllers.reportes.resumen_biblioteca(db)
