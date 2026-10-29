from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.dependencies import Pagina, Paginacion, armar_pagina
from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.core.security import hashear_password
from app.models.entities import Socio
from app.models.refresh_token import RefreshToken
from app.models.usuario import RolUsuario, Usuario
from app.schemas.usuario import (
    UsuarioCambiarActivo,
    UsuarioCambiarRol,
    UsuarioCrear,
    UsuarioRespuesta,
)


def listar_usuarios(
    db: Session,
    paginacion: Paginacion,
    rol: RolUsuario | None = None,
    activo: bool | None = None,
) -> Pagina[UsuarioRespuesta]:
    consulta = select(Usuario)
    if rol is not None:
        consulta = consulta.where(Usuario.rol == rol)
    if activo is not None:
        consulta = consulta.where(Usuario.activo.is_(activo))

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    usuarios = list(
        db.scalars(
            consulta.order_by(Usuario.id)
            .offset(paginacion.skip)
            .limit(paginacion.limit)
        ).all()
    )
    items = [UsuarioRespuesta.model_validate(u) for u in usuarios]
    return armar_pagina(items, total, paginacion)


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NoEncontrado("Usuario no encontrado")
    return usuario


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    email_lower = datos.email.lower()
    if db.scalar(select(Usuario.id).where(Usuario.email == email_lower)):
        raise Conflicto("El correo electrónico ya está registrado")

    nuevo = Usuario(
        email=email_lower,
        nombre=datos.nombre.title(),
        password_hash=hashear_password(datos.password),
        rol=datos.rol,
        activo=True,
        socio_id=None,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def _contar_admins_activos_excluyendo(db: Session, excluir_id: int) -> int:
    return (
        db.scalar(
            select(func.count(Usuario.id)).where(
                Usuario.rol == RolUsuario.admin,
                Usuario.activo.is_(True),
                Usuario.id != excluir_id,
            )
        )
        or 0
    )


def cambiar_rol_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioCambiarRol,
    admin_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)

    # Regla Z5: Un admin no puede quitarse el rol a sí mismo y siempre debe quedar al menos 1 admin activo
    if usuario.id == admin_actual.id and datos.rol != RolUsuario.admin:
        raise ReglaNegocio(
            "Un administrador no puede quitarse el rol de administrador a sí mismo"
        )

    if (
        usuario.rol == RolUsuario.admin
        and datos.rol != RolUsuario.admin
        and _contar_admins_activos_excluyendo(db, usuario.id) == 0
    ):
        raise ReglaNegocio("Debe existir al menos un administrador activo")

    usuario.rol = datos.rol

    # Regla Z6: Cambiar el rol revoca todos los refresh tokens del usuario
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id)
        .values(revocado=True)
    )
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_activo_usuario(
    db: Session,
    usuario_id: int,
    datos: UsuarioCambiarActivo,
    admin_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)

    # Regla Z5: Un admin no puede desactivarse a sí mismo y siempre debe quedar al menos 1 admin activo
    if usuario.id == admin_actual.id and not datos.activo:
        raise ReglaNegocio("Un administrador no puede desactivarse a sí mismo")

    if (
        usuario.rol == RolUsuario.admin
        and not datos.activo
        and _contar_admins_activos_excluyendo(db, usuario.id) == 0
    ):
        raise ReglaNegocio("Debe existir al menos un administrador activo")

    usuario.activo = datos.activo
    if usuario.socio_id is not None:
        socio = db.get(Socio, usuario.socio_id)
        if socio is not None:
            socio.activo = datos.activo

    # Regla Z6: Desactivar (o cambiar estado) revoca todos los refresh tokens del usuario
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id)
        .values(revocado=True)
    )
    db.commit()
    db.refresh(usuario)
    return usuario

