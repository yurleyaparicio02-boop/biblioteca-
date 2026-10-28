from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.dependencias import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Prestamo, Socio
from ..schemas.prestamos import EstadoPrestamo
from ..schemas.socios import SocioActualizar, SocioCrear, SocioResponse
from .prestamos import _respuesta, aplicar_filtro_estado


def listar_socios(
    db: Session, paginacion: Paginacion, activo: bool | None = None
) -> Pagina[SocioResponse]:
    consulta = select(Socio)
    if activo is not None:
        consulta = consulta.where(Socio.activo.is_(activo))
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    socios = list(
        db.scalars(
            consulta.order_by(Socio.id)
            .offset(paginacion.skip)
            .limit(paginacion.limit)
        ).all()
    )
    items = [SocioResponse.model_validate(socio) for socio in socios]
    return armar_pagina(items, total, paginacion)


def obtener_socio(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    return socio


def crear_socio(db: Session, datos: SocioCrear) -> Socio:
    if db.scalar(select(Socio.id).where(Socio.email == str(datos.email))):
        raise Conflicto("El correo electrónico ya está registrado")
    socio = Socio(**datos.model_dump())
    db.add(socio)
    db.commit()
    db.refresh(socio)
    return socio


def actualizar_socio(
    db: Session, socio_id: int, datos: SocioActualizar
) -> Socio:
    socio = obtener_socio(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("email") is not None:
        duplicado = db.scalar(
            select(Socio.id).where(
                Socio.email == str(cambios["email"]), Socio.id != socio_id
            )
        )
        if duplicado:
            raise Conflicto("El correo electrónico ya está registrado")
    for campo, valor in cambios.items():
        setattr(socio, campo, str(valor) if campo == "email" and valor else valor)
    db.commit()
    db.refresh(socio)
    return socio


def eliminar_socio(db: Session, socio_id: int) -> None:
    socio = obtener_socio(db, socio_id)
    tiene_prestamos_abiertos = db.scalar(
        select(Prestamo.id)
        .where(
            Prestamo.socio_id == socio_id,
            Prestamo.fecha_devolucion.is_(None),
        )
        .limit(1)
    )
    if tiene_prestamos_abiertos:
        raise Conflicto("No se puede eliminar el socio porque tiene préstamos activos")
    tiene_historial = db.scalar(
        select(Prestamo.id).where(Prestamo.socio_id == socio_id).limit(1)
    )
    if tiene_historial:
        socio.activo = False
    else:
        db.delete(socio)
    db.commit()


def listar_prestamos_socio(
    db: Session,
    socio_id: int,
    paginacion: Paginacion,
    estado: EstadoPrestamo | None = None,
) -> Pagina[dict[str, object]]:
    obtener_socio(db, socio_id)
    base = aplicar_filtro_estado(
        select(Prestamo).where(Prestamo.socio_id == socio_id), estado
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    consulta = (
        base.order_by(Prestamo.id)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    )
    items = [_respuesta(prestamo) for prestamo in db.scalars(consulta).all()]
    return armar_pagina(items, total, paginacion)
