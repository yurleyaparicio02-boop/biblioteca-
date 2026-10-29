from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def validar_reglas_password(v: str) -> str:
    if not any(c.isupper() for c in v):
        raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not any(c.islower() for c in v):
        raise ValueError("La contraseña debe tener al menos una minúscula")
    if not any(c.isdigit() for c in v):
        raise ValueError("La contraseña debe tener al menos un número")
    return v


def _validar_telefono(value: str | None) -> str | None:
    if value is not None and any(char not in "0123456789 +" for char in value):
        raise ValueError("El teléfono solo puede contener dígitos, espacios o +")
    return value


class UsuarioRegistro(BaseModel):
    email: EmailStr = Field(max_length=150)
    nombre: str = Field(min_length=3, max_length=100)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)
    password: str = Field(min_length=8, max_length=64)
    confirmar_password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

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

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        return validar_reglas_password(v)

    @model_validator(mode="after")
    def validar_coincidencia(self) -> "UsuarioRegistro":
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class TokenRespuesta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


LoginRespuesta = TokenRespuesta


class RefreshPeticion(BaseModel):
    refresh_token: str


class CambiarPasswordPeticion(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8, max_length=64)

    @field_validator("password_nueva")
    @classmethod
    def validar_password(cls, v: str) -> str:
        return validar_reglas_password(v)
