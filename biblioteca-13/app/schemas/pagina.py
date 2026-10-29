from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    """Respuesta paginada genérica."""

    items: list[T]
    total: int
    skip: int
    limit: int

