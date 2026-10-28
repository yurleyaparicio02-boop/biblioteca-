from typing import Annotated

from fastapi import APIRouter, Depends, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import PaginacionDep, Pagina
from ..schemas.libros import (
    FiltroLibros,
    LibroActualizar,
    LibroCrear,
    LibroResponse,
)

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=Pagina[LibroResponse])
def listar_libros(
    db: SessionDep,
    paginacion: PaginacionDep,
    filtros: Annotated[FiltroLibros, Depends()],
):
    return controllers.libros.listar_libros(db, paginacion, filtros)


@router.get("/{libro_id}", response_model=LibroResponse)
def obtener_libro(libro_id: int, db: SessionDep):
    return controllers.libros.obtener_libro(db, libro_id)


@router.post("", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCrear, db: SessionDep):
    return controllers.libros.crear_libro(db, datos)


@router.patch("/{libro_id}", response_model=LibroResponse)
def actualizar_libro(
    libro_id: int, datos: LibroActualizar, db: SessionDep
):
    return controllers.libros.actualizar_libro(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, db: SessionDep) -> None:
    controllers.libros.eliminar_libro(db, libro_id)
