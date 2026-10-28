from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("descripcion", mode="before")
    @classmethod
    def limpiar_descripcion(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class CategoriaCrear(CategoriaBase):
    pass


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @model_validator(mode="before")
    @classmethod
    def nombre_no_nulo(cls, value: object) -> object:
        if isinstance(value, dict) and value.get("nombre", "omitido") is None:
            raise ValueError("nombre no puede ser null")
        return value

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("descripcion", mode="before")
    @classmethod
    def limpiar_descripcion(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class CategoriaResumen(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class CategoriaResponse(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
