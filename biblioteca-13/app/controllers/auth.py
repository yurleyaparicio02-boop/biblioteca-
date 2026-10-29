from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    Conflicto,
    CuentaBloqueada,
    NoAutenticado,
    Prohibido,
)
from app.core.security import (
    crear_token,
    decodificar_token,
    hashear_password,
    verificar_password,
)
from app.models.entities import Socio
from app.models.refresh_token import RefreshToken
from app.models.usuario import RolUsuario, Usuario
from app.schemas.auth import CambiarPasswordPeticion, UsuarioRegistro


def _asegurar_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def registrar_usuario(db: Session, datos: UsuarioRegistro) -> Usuario:
    email_lower = datos.email.lower()

    usuario_existente = db.scalar(
        select(Usuario).where(Usuario.email == email_lower)
    )
    if usuario_existente:
        raise Conflicto("El correo ya está registrado en el sistema")

    socio_existente = db.scalar(
        select(Socio).where(Socio.email == email_lower)
    )
    if socio_existente:
        raise Conflicto("El correo ya está registrado como socio")

    try:
        nuevo_socio = Socio(
            nombre=datos.nombre.title(),
            email=email_lower,
            telefono=datos.telefono,
            activo=True,
        )
        db.add(nuevo_socio)
        db.flush()

        nuevo_usuario = Usuario(
            email=email_lower,
            nombre=datos.nombre.title(),
            password_hash=hashear_password(datos.password),
            rol=RolUsuario.socio,
            activo=True,
            socio_id=nuevo_socio.id,
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except Exception:
        db.rollback()
        raise


def iniciar_sesion(
    db: Session, username: str, password: str
) -> dict[str, object]:
    settings = get_settings()
    email = username.strip().lower()
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))

    # Regla A1: Mensaje idéntico si el email no existe o contraseña incorrecta
    if not usuario:
        raise NoAutenticado("Credenciales inválidas")

    ahora_utc = datetime.now(timezone.utc)
    bloqueado_hasta = _asegurar_utc(usuario.bloqueado_hasta)

    # Regla A3: Bloqueo temporal por intentos fallidos
    if bloqueado_hasta and bloqueado_hasta > ahora_utc:
        raise CuentaBloqueada("Cuenta bloqueada temporalmente")

    if not verificar_password(password, usuario.password_hash):
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= 5:
            usuario.bloqueado_hasta = ahora_utc + timedelta(minutes=15)
        db.commit()
        raise NoAutenticado("Credenciales inválidas")

    # Regla A2: El usuario debe estar activo (403)
    if not usuario.activo:
        raise Prohibido("Usuario inactivo")

    # Login correcto: reiniciar intentos fallidos
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None

    access_token, _ = crear_token(
        usuario, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token_str, refresh_jti = crear_token(
        usuario, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )

    nuevo_refresh = RefreshToken(
        jti=refresh_jti,
        usuario_id=usuario.id,
        expira_en=ahora_utc + timedelta(days=settings.refresh_token_expire_days),
        revocado=False,
    )
    db.add(nuevo_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


def renovar_token(db: Session, refresh_token_str: str) -> dict[str, object]:
    settings = get_settings()
    payload = decodificar_token(refresh_token_str, tipo_esperado="refresh")

    jti = payload.get("jti")
    user_id_str = payload.get("sub")
    if not jti or not user_id_str:
        raise NoAutenticado("Refresh token inválido")

    db_token = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if db_token is None:
        raise NoAutenticado("Refresh token no registrado")

    # Regla A6: Si se reutiliza un refresh token ya revocado, se revocan todos los del usuario
    if db_token.revocado:
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.usuario_id == db_token.usuario_id)
            .values(revocado=True)
        )
        db.commit()
        raise NoAutenticado("Refresh token inválido o reutilizado")

    ahora_utc = datetime.now(timezone.utc)
    expira_en = _asegurar_utc(db_token.expira_en)
    if expira_en and expira_en < ahora_utc:
        raise NoAutenticado("Refresh token vencido")

    usuario = db.get(Usuario, int(user_id_str))
    if not usuario:
        raise NoAutenticado("Usuario no encontrado")
    if not usuario.activo:
        raise Prohibido("Usuario inactivo")

    # Rotación: revocar el token recibido y emitir un par nuevo
    db_token.revocado = True

    nuevo_access, _ = crear_token(
        usuario, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    nuevo_refresh_str, nuevo_jti = crear_token(
        usuario, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )

    nuevo_db_refresh = RefreshToken(
        jti=nuevo_jti,
        usuario_id=usuario.id,
        expira_en=ahora_utc + timedelta(days=settings.refresh_token_expire_days),
        revocado=False,
    )
    db.add(nuevo_db_refresh)
    db.commit()

    return {
        "access_token": nuevo_access,
        "refresh_token": nuevo_refresh_str,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


def cerrar_sesion(db: Session, refresh_token_str: str) -> None:
    payload = decodificar_token(refresh_token_str, tipo_esperado="refresh")
    jti = payload.get("jti")
    if not jti:
        raise NoAutenticado("Refresh token inválido")

    db_token = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if db_token is None:
        raise NoAutenticado("Refresh token no encontrado")

    db_token.revocado = True
    db.commit()


def cambiar_password(
    db: Session, usuario: Usuario, datos: CambiarPasswordPeticion
) -> Usuario:
    if not verificar_password(datos.password_actual, usuario.password_hash):
        raise NoAutenticado("La contraseña actual es incorrecta")

    usuario.password_hash = hashear_password(datos.password_nueva)
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id)
        .values(revocado=True)
    )
    db.commit()
    db.refresh(usuario)
    return usuario
