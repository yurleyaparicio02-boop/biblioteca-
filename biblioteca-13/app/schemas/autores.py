from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AutorBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000, le=date.today().year)

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("nacionalidad", mode="before")
    @classmethod
    def limpiar_nacionalidad(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class AutorCrear(AutorBase):
    pass


class AutorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000, le=date.today().year)

    @model_validator(mode="before")
    @classmethod
    def nombre_no_nulo(cls, value: object) -> object:
        if isinstance(value, dict) and value.get("nombre", "omitido") is None:
            raise ValueError("nombre no puede ser null")
        return value

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("nacionalidad", mode="before")
    @classmethod
    def limpiar_nacionalidad(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class AutorResumen(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class AutorResponse(AutorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
