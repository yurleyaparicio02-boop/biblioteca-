from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.usuario import RolUsuario
from app.schemas.auth import validar_reglas_password


class UsuarioRespuesta(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    rol: RolUsuario
    activo: bool
    socio_id: int | None
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioCrear(BaseModel):
    email: EmailStr = Field(max_length=150)
    nombre: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=64)
    rol: RolUsuario = RolUsuario.bibliotecario

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, value: object) -> object:
        return value.strip().title() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        return validar_reglas_password(v)

    @field_validator("rol")
    @classmethod
    def validar_rol_staff(cls, v: RolUsuario) -> RolUsuario:
        if v not in (RolUsuario.admin, RolUsuario.bibliotecario):
            raise ValueError("Solo se pueden crear usuarios con rol bibliotecario o admin")
        return v


class UsuarioCambiarRol(BaseModel):
    rol: RolUsuario


class UsuarioCambiarActivo(BaseModel):
    activo: bool
