from dataclasses import dataclass
from math import ceil
from typing import Annotated, Generic, TypeVar

from fastapi import Depends, Query
from pydantic import BaseModel

T = TypeVar("T")


@dataclass(frozen=True)
class Paginacion:
    skip: int
    limit: int


def get_paginacion(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Paginacion:
    return Paginacion(skip=skip, limit=limit)


PaginacionDep = Annotated[Paginacion, Depends(get_paginacion)]


class Pagina(BaseModel, Generic[T]):
    """Respuesta paginada genérica.

    ``skip`` y ``limit`` describen la petición, ``total`` el número de
    registros que cumplen el filtro (no el de la página) y ``paginas`` el
    total de páginas con el ``limit`` solicitado.
    """

    items: list[T]
    total: int
    skip: int
    limit: int
    paginas: int


def armar_pagina(
    items: list[T], total: int, paginacion: Paginacion
) -> Pagina[T]:
    return Pagina[T](
        items=items,
        total=total,
        skip=paginacion.skip,
        limit=paginacion.limit,
        paginas=ceil(total / paginacion.limit) if total else 0,
    )
