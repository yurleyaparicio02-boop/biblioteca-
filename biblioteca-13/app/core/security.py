from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from pwdlib import PasswordHash
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.exceptions import NoAutenticado
from app.models.usuario import Usuario

settings = get_settings()
password_hash = PasswordHash.recommended()  # Argon2
limiter = Limiter(key_func=get_remote_address)


def hashear_password(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    return password_hash.verify(password, hash_guardado)


def crear_token(usuario: Usuario, tipo: str, duracion: timedelta) -> tuple[str, str]:
    ahora = datetime.now(timezone.utc)
    jti = str(uuid4())
    payload = {
        "sub": str(usuario.id),
        "rol": usuario.rol.value,
        "type": tipo,
        "iat": ahora,
        "exp": ahora + duracion,
        "jti": jti,
    }
    return (
        jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm),
        jti,
    )


def decodificar_token(token: str, tipo_esperado: str | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except jwt.InvalidTokenError as exc:
        raise NoAutenticado("Token inválido o vencido") from exc

    if tipo_esperado is not None and payload.get("type") != tipo_esperado:
        raise NoAutenticado("Tipo de token inválido")
    return payload
