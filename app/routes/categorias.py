from fastapi import APIRouter, status

from .. import controllers
from ..core.database import SessionDep
from ..core.dependencias import PaginacionDep, Pagina
from ..schemas.categorias import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaResponse,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=Pagina[CategoriaResponse])
def listar_categorias(db: SessionDep, paginacion: PaginacionDep):
    return controllers.categorias.listar_categorias(db, paginacion)


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: SessionDep):
    return controllers.categorias.obtener_categoria(db, categoria_id)


@router.post(
    "", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED
)
def crear_categoria(datos: CategoriaCrear, db: SessionDep):
    return controllers.categorias.crear_categoria(db, datos)


@router.patch("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(
    categoria_id: int, datos: CategoriaActualizar, db: SessionDep
):
    return controllers.categorias.actualizar_categoria(db, categoria_id, datos)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: SessionDep) -> None:
    controllers.categorias.eliminar_categoria(db, categoria_id)
