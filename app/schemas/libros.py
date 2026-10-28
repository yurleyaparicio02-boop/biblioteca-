from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .autores import AutorResumen
from .categorias import CategoriaResumen


class OrdenLibros(str, Enum):
    titulo = "titulo"
    anio = "anio"
    anio_desc = "-anio"


class LibroCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    isbn: str = Field(pattern=r"^\d{13}$")
    anio_publicacion: int = Field(ge=1450, le=date.today().year)
    ejemplares: int = Field(ge=1, le=50)
    autor_id: int = Field(gt=0)
    categoria_ids: list[int] = Field(min_length=1, max_length=5)

    @field_validator("titulo", mode="before")
    @classmethod
    def normalizar_titulo(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("categoria_ids")
    @classmethod
    def categorias_sin_repetir(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("categoria_ids no puede contener valores repetidos")
        return value


class LibroActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")
    anio_publicacion: int | None = Field(
        default=None, ge=1450, le=date.today().year
    )
    ejemplares: int | None = Field(default=None, ge=1, le=50)
    autor_id: int | None = Field(default=None, gt=0)
    categoria_ids: list[int] | None = Field(default=None, min_length=1, max_length=5)

    @model_validator(mode="before")
    @classmethod
    def valores_no_nulos(cls, value: object) -> object:
        if isinstance(value, dict):
            for campo in (
                "titulo",
                "isbn",
                "anio_publicacion",
                "ejemplares",
                "autor_id",
                "categoria_ids",
            ):
                if campo in value and value[campo] is None:
                    raise ValueError(f"{campo} no puede ser null")
        return value

    @field_validator("titulo", mode="before")
    @classmethod
    def normalizar_titulo(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("categoria_ids")
    @classmethod
    def categorias_sin_repetir(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("categoria_ids no puede contener valores repetidos")
        return value


class LibroResumen(BaseModel):
    id: int
    titulo: str
    isbn: str
    anio_publicacion: int
    ejemplares: int
    model_config = ConfigDict(from_attributes=True)


class LibroResponse(LibroResumen):
    disponibles: int
    autor: AutorResumen
    categorias: list[CategoriaResumen]


class FiltroLibros(BaseModel):
    buscar: str | None = None
    autor: str | None = None
    categoria_id: int | None = Field(default=None, gt=0)
    desde: int | None = Field(default=None, ge=1450, le=date.today().year)
    hasta: int | None = Field(default=None, ge=1450, le=date.today().year)
    orden: OrdenLibros = OrdenLibros.titulo

    @model_validator(mode="after")
    def validar_rango(self) -> "FiltroLibros":
        if self.desde is not None and self.hasta is not None and self.desde > self.hasta:
            raise ValueError("desde no puede ser mayor que hasta")
        return self
