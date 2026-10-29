from dataclasses import dataclass
from typing import Annotated, Any, TypeVar

import jwt
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings
from app.core.database import SessionDep, get_db
from app.core.exceptions import NoAutenticado, Prohibido
from app.models.usuario import RolUsuario, Usuario
from app.schemas.pagina import Pagina

T = TypeVar("T")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="Inicio de sesión con Correo y Contraseña (JWT)",
    description=(
        "Ingresa tu **correo electrónico** en el campo `username` y tu "
        "**contraseña** en `password`. Deja vacíos `client_id` y `client_secret`."
    ),
    auto_error=False,
)


@dataclass(frozen=True)
class Paginacion:
    skip: int
    limit: int


def get_paginacion(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> Paginacion:
    return Paginacion(skip=skip, limit=limit)


PaginacionDep = Annotated[Paginacion, Depends(get_paginacion)]


def armar_pagina(
    items: list[T], total: int, paginacion: Paginacion
) -> Pagina[T]:
    return Pagina[T](
        items=items,
        total=total,
        skip=paginacion.skip,
        limit=paginacion.limit,
    )


def get_current_user(
    db: SessionDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> Usuario:
    if not token:
        raise NoAutenticado("No se proporcionó token de autenticación")

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except jwt.InvalidTokenError as exc:
        raise NoAutenticado("Token inválido o vencido") from exc

    if payload.get("type") != "access":
        raise NoAutenticado("Tipo de token inválido")

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise NoAutenticado("Token inválido") from exc

    usuario = db.get(Usuario, user_id)
    if usuario is None:
        raise NoAutenticado("Usuario no encontrado")

    if not usuario.activo:
        raise Prohibido("Usuario inactivo")

    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def requiere_rol(*roles: RolUsuario) -> Any:
    def verificar(usuario: CurrentUser) -> Usuario:
        if usuario.rol not in roles:
            raise Prohibido("No tiene permisos para esta acción")
        return usuario

    return Depends(verificar)


Staff = Annotated[Usuario, requiere_rol(RolUsuario.admin, RolUsuario.bibliotecario)]

__all__ = [
    "SessionDep",
    "get_db",
    "Paginacion",
    "PaginacionDep",
    "Pagina",
    "get_paginacion",
    "armar_pagina",
    "oauth2_scheme",
    "get_current_user",
    "CurrentUser",
    "requiere_rol",
    "Staff",
]

