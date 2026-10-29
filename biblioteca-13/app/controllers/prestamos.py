from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.dependencies import Paginacion, Pagina, armar_pagina
from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Libro, Prestamo, RolUsuario, Socio, Usuario
from ..schemas.prestamos import (
    DevolucionCrear,
    EstadoMulta,
    EstadoPrestamo,
    PrestamoCrear,
)

# Multa por cada día de retraso sobre fecha_limite.
MULTA_POR_DIA = Decimal("0.50")


def estado_prestamo(prestamo: Prestamo, hoy: date | None = None) -> EstadoPrestamo:
    if prestamo.fecha_devolucion is not None:
        return EstadoPrestamo.devuelto
    return (
        EstadoPrestamo.vencido
        if prestamo.fecha_limite < (hoy or date.today())
        else EstadoPrestamo.activo
    )


def estado_multa(prestamo: Prestamo) -> EstadoMulta:
    if prestamo.multa <= 0:
        return EstadoMulta.sin_multa
    return EstadoMulta.pagada if prestamo.multa_pagada else EstadoMulta.pendiente


def multas_pendientes(db: Session, socio_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Prestamo.multa), 0)).where(
            Prestamo.socio_id == socio_id,
            Prestamo.multa > 0,
            Prestamo.multa_pagada.is_(False),
        )
    )
    return Decimal(total or 0)


def aplicar_filtro_estado(consulta, estado: EstadoPrestamo | None):
    if estado == EstadoPrestamo.devuelto:
        return consulta.where(Prestamo.fecha_devolucion.is_not(None))
    if estado == EstadoPrestamo.vencido:
        return consulta.where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < date.today(),
        )
    if estado == EstadoPrestamo.activo:
        return consulta.where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite >= date.today(),
        )
    return consulta


def _respuesta(prestamo: Prestamo) -> dict[str, object]:
    return {
        "id": prestamo.id,
        "libro_id": prestamo.libro_id,
        "socio_id": prestamo.socio_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_limite": prestamo.fecha_limite,
        "fecha_devolucion": prestamo.fecha_devolucion,
        "multa": prestamo.multa,
        "multa_pagada": prestamo.multa_pagada,
        "estado_multa": estado_multa(prestamo),
        "estado": estado_prestamo(prestamo),
        "registrado_por_id": prestamo.registrado_por_id,
    }


def _detalle(prestamo: Prestamo) -> dict[str, object]:
    return {
        **_respuesta(prestamo),
        "libro": prestamo.libro,
        "socio": prestamo.socio,
    }


def listar_prestamos(
    db: Session,
    paginacion: Paginacion,
    estado: EstadoPrestamo | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None,
    usuario: Usuario | None = None,
) -> Pagina[dict[str, object]]:
    consulta = aplicar_filtro_estado(select(Prestamo), estado)
    # Regla Z3: En GET /prestamos un socio solo recibe sus préstamos aunque envíe ?socio_id= de otro
    if usuario is not None and usuario.rol == RolUsuario.socio:
        consulta = consulta.where(Prestamo.socio_id == usuario.socio_id)
    elif socio_id is not None:
        consulta = consulta.where(Prestamo.socio_id == socio_id)

    if libro_id is not None:
        consulta = consulta.where(Prestamo.libro_id == libro_id)
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    consulta = (
        consulta.order_by(Prestamo.id)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    )
    items = [_respuesta(prestamo) for prestamo in db.scalars(consulta).all()]
    return armar_pagina(items, total, paginacion)


def obtener_prestamo(
    db: Session, prestamo_id: int, usuario: Usuario | None = None
) -> dict[str, object]:
    consulta = (
        select(Prestamo)
        .options(selectinload(Prestamo.libro), selectinload(Prestamo.socio))
        .where(Prestamo.id == prestamo_id)
    )
    # Regla Z2: Un socio que consulta un préstamo que no es suyo recibe 404, no 403
    if usuario is not None and usuario.rol == RolUsuario.socio:
        consulta = consulta.where(Prestamo.socio_id == usuario.socio_id)

    prestamo = db.scalar(consulta)
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    return _detalle(prestamo)


def registrar_prestamo(
    db: Session,
    datos: PrestamoCrear,
    registrado_por_id: int | None = None,
) -> dict[str, object]:
    socio = db.get(Socio, datos.socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")
    hoy = date.today()
    deuda = multas_pendientes(db, socio.id)
    if deuda > 0:
        raise ReglaNegocio("El socio tiene multas pendientes")
    prestamos_abiertos = select(Prestamo).where(
        Prestamo.socio_id == socio.id,
        Prestamo.fecha_devolucion.is_(None),
    )
    if db.scalar(
        select(Prestamo.id).where(
            Prestamo.socio_id == socio.id,
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < hoy,
        )
    ):
        raise ReglaNegocio("El socio tiene préstamos vencidos")
    cantidad_abiertos = (
        db.scalar(
            select(func.count()).select_from(prestamos_abiertos.subquery())
        )
        or 0
    )
    if cantidad_abiertos >= 3:
        raise ReglaNegocio("Máximo de 3 préstamos")
    if db.scalar(
        select(Prestamo.id).where(
            Prestamo.socio_id == socio.id,
            Prestamo.libro_id == libro.id,
            Prestamo.fecha_devolucion.is_(None),
        )
    ):
        raise Conflicto("El socio ya tiene este libro sin devolver")
    if datos.fecha_prestamo > hoy:
        raise ReglaNegocio("La fecha de préstamo no puede ser futura")

    libro = db.scalar(
        select(Libro).where(Libro.id == datos.libro_id).with_for_update()
    )
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    cantidad_libro_abiertos = (
        db.scalar(
            select(func.count(Prestamo.id)).where(
                Prestamo.libro_id == libro.id,
                Prestamo.fecha_devolucion.is_(None),
            )
        )
        or 0
    )
    if libro.ejemplares - cantidad_libro_abiertos <= 0:
        db.rollback()
        raise ReglaNegocio("No hay ejemplares disponibles")

    prestamo = Prestamo(
        libro_id=libro.id,
        socio_id=socio.id,
        fecha_prestamo=datos.fecha_prestamo,
        fecha_limite=datos.fecha_prestamo + timedelta(days=datos.dias),
        multa=Decimal("0.00"),
        multa_pagada=True,
        registrado_por_id=registrado_por_id,
    )
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return _respuesta(prestamo)


def registrar_devolucion(
    db: Session, prestamo_id: int, datos: DevolucionCrear
) -> dict[str, object]:
    prestamo = db.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto")
    if datos.fecha_devolucion < prestamo.fecha_prestamo:
        raise ReglaNegocio("La fecha de devolución no puede ser anterior al préstamo")
    if datos.fecha_devolucion > date.today():
        raise ReglaNegocio("La fecha de devolución no puede ser futura")
    dias_retraso = max((datos.fecha_devolucion - prestamo.fecha_limite).days, 0)
    prestamo.fecha_devolucion = datos.fecha_devolucion
    prestamo.multa = (Decimal(dias_retraso) * MULTA_POR_DIA).quantize(Decimal("0.01"))
    prestamo.multa_pagada = prestamo.multa == Decimal("0.00")
    db.commit()
    db.refresh(prestamo)
    return _respuesta(prestamo)


def pagar_multa(db: Session, prestamo_id: int) -> dict[str, object]:
    """Marca como pagada la multa de un préstamo devuelto."""
    prestamo = db.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    if prestamo.multa <= 0:
        raise Conflicto("El préstamo no tiene multa")
    if prestamo.multa_pagada:
        raise Conflicto("La multa ya fue pagada")
    prestamo.multa_pagada = True
    db.commit()
    db.refresh(prestamo)
    return _respuesta(prestamo)
