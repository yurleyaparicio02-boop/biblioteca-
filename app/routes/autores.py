from typing import Annotated

from fastapi import APIRouter, Query, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import PaginacionDep, Pagina
from ..schemas.autores import AutorActualizar, AutorCrear, AutorResponse
from ..schemas.libros import LibroResponse

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("", response_model=Pagina[AutorResponse])
def listar_autores(
    db: SessionDep,
    paginacion: PaginacionDep,
    nacionalidad: Annotated[str | None, Query(max_length=60)] = None,
):
    return controllers.autores.listar_autores(db, paginacion, nacionalidad)


@router.get("/{autor_id}", response_model=AutorResponse)
def obtener_autor(autor_id: int, db: SessionDep):
    return controllers.autores.obtener_autor(db, autor_id)


@router.get("/{autor_id}/libros", response_model=Pagina[LibroResponse])
def listar_libros_autor(
    autor_id: int, db: SessionDep, paginacion: PaginacionDep
):
    return controllers.autores.listar_libros_autor(db, autor_id, paginacion)


@router.post("", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCrear, db: SessionDep):
    return controllers.autores.crear_autor(db, datos)


@router.patch("/{autor_id}", response_model=AutorResponse)
def actualizar_autor(autor_id: int, datos: AutorActualizar, db: SessionDep):
    return controllers.autores.actualizar_autor(db, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, db: SessionDep) -> None:
    controllers.autores.eliminar_autor(db, autor_id)
