from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def _validar_telefono(value: str | None) -> str | None:
    if value is not None and any(char not in "0123456789 +" for char in value):
        raise ValueError("El teléfono solo puede contener dígitos, espacios o +")
    return value


class SocioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=150)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("telefono", mode="before")
    @classmethod
    def limpiar_telefono(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("telefono")
    @classmethod
    def validar_formato_telefono(cls, value: str | None) -> str | None:
        return _validar_telefono(value)


class SocioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)
    activo: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def valores_no_nulos(cls, value: object) -> object:
        if isinstance(value, dict):
            for campo in ("nombre", "email", "activo"):
                if campo in value and value[campo] is None:
                    raise ValueError(f"{campo} no puede ser null")
        return value

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("telefono", mode="before")
    @classmethod
    def limpiar_telefono(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("telefono")
    @classmethod
    def validar_formato_telefono(cls, value: str | None) -> str | None:
        return _validar_telefono(value)


class SocioActualizarPropio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)

    @model_validator(mode="before")
    @classmethod
    def nombre_no_nulo(cls, value: object) -> object:
        if isinstance(value, dict) and "nombre" in value and value["nombre"] is None:
            raise ValueError("nombre no puede ser null")
        return value

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("telefono", mode="before")
    @classmethod
    def limpiar_telefono(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("telefono")
    @classmethod
    def validar_formato_telefono(cls, value: str | None) -> str | None:
        return _validar_telefono(value)


class SocioResumen(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class SocioResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    activo: bool
    fecha_alta: datetime
    model_config = ConfigDict(from_attributes=True)
