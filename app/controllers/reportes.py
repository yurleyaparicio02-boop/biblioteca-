from datetime import date
from decimal import Decimal

from sqlalchemy import Integer, case, cast, distinct, func, select
from sqlalchemy.orm import Session

from ..core.dependencias import Paginacion, Pagina, armar_pagina
from ..models import Autor, Categoria, Libro, Prestamo, Socio, libro_categoria
from ..schemas.reportes import (
    LibrosPorCategoria,
    LibroMasPrestado,
    PrestamoVencidoReporte,
    ReporteAutor,
    ResumenBiblioteca,
    SocioMultas,
)


def libros_mas_prestados(
    db: Session, limite: int, skip: int = 0
) -> Pagina[LibroMasPrestado]:
    paginacion = Paginacion(skip=skip, limit=limite)
    consulta = (
        select(
            Libro.id.label("libro_id"),
            Libro.titulo,
            Autor.nombre.label("autor"),
            func.count(Prestamo.id).label("total_prestamos"),
        )
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .join(Autor, Autor.id == Libro.autor_id)
        .group_by(Libro.id, Libro.titulo, Autor.id, Autor.nombre)
    )
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = db.execute(
        consulta.order_by(func.count(Prestamo.id).desc(), Libro.id)
        .offset(skip)
        .limit(limite)
    ).mappings()
    items = [LibroMasPrestado(**row) for row in filas]
    return armar_pagina(items, total, paginacion)


def categorias_con_libros(
    db: Session, paginacion: Paginacion
) -> Pagina[LibrosPorCategoria]:
    total_registros = (
        db.scalar(select(func.count()).select_from(Categoria)) or 0
    )
    total = func.count(libro_categoria.c.libro_id).label("total_libros")
    consulta = (
        select(
            Categoria.id.label("categoria_id"),
            Categoria.nombre.label("categoria"),
            total,
        )
        .outerjoin(
            libro_categoria, libro_categoria.c.categoria_id == Categoria.id
        )
        .group_by(Categoria.id, Categoria.nombre)
        .order_by(Categoria.nombre)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    )
    items = [LibrosPorCategoria(**row) for row in db.execute(consulta).mappings()]
    return armar_pagina(items, total_registros, paginacion)


def prestamos_vencidos(
    db: Session, paginacion: Paginacion
) -> Pagina[PrestamoVencidoReporte]:
    dias_retraso = func.current_date() - Prestamo.fecha_limite
    base = (
        select(
            Prestamo.id.label("prestamo_id"),
            Libro.titulo,
            Socio.nombre.label("socio"),
            Socio.email,
            Prestamo.fecha_limite,
            cast(dias_retraso, Integer).label("dias_retraso"),
        )
        .join(Libro, Libro.id == Prestamo.libro_id)
        .join(Socio, Socio.id == Prestamo.socio_id)
        .where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < date.today(),
        )
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    consulta = (
        base.order_by(Prestamo.fecha_limite)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    )
    items = [
        PrestamoVencidoReporte(**row) for row in db.execute(consulta).mappings()
    ]
    return armar_pagina(items, total, paginacion)


def socios_con_multas(
    db: Session, paginacion: Paginacion, solo_pendientes: bool = True
) -> Pagina[SocioMultas]:
    filtros = [Prestamo.multa > 0]
    if solo_pendientes:
        filtros.append(Prestamo.multa_pagada.is_(False))
    suma_multas = func.sum(Prestamo.multa).label("total_multas")
    cantidad_multas = func.count(
        case((Prestamo.multa > 0, Prestamo.id))
    ).label("prestamos_con_multa")
    base = (
        select(
            Socio.id.label("socio_id"),
            Socio.nombre.label("socio"),
            suma_multas,
            cantidad_multas,
        )
        .join(Prestamo, Prestamo.socio_id == Socio.id)
        .where(*filtros)
        .group_by(Socio.id, Socio.nombre)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    consulta = (
        base.order_by(suma_multas.desc(), Socio.id)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    )
    items = [SocioMultas(**row) for row in db.execute(consulta).mappings()]
    return armar_pagina(items, total, paginacion)


def reporte_autores(
    db: Session, paginacion: Paginacion
) -> Pagina[ReporteAutor]:
    libros_por_autor = (
        select(
            Libro.autor_id.label("autor_id"),
            func.count(distinct(Libro.id)).label("total_libros"),
            func.coalesce(func.sum(Libro.ejemplares), 0).label("total_ejemplares"),
        )
        .group_by(Libro.autor_id)
        .subquery()
    )
    prestamos_por_autor = (
        select(
            Libro.autor_id.label("autor_id"),
            func.count(Prestamo.id).label("total_prestamos"),
        )
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Libro.autor_id)
        .subquery()
    )
    consulta = (
        select(
            Autor.id.label("autor_id"),
            Autor.nombre.label("autor"),
            func.coalesce(libros_por_autor.c.total_libros, 0).label("total_libros"),
            func.coalesce(libros_por_autor.c.total_ejemplares, 0).label(
                "total_ejemplares"
            ),
            func.coalesce(prestamos_por_autor.c.total_prestamos, 0).label(
                "total_prestamos"
            ),
        )
        .outerjoin(libros_por_autor, libros_por_autor.c.autor_id == Autor.id)
        .outerjoin(prestamos_por_autor, prestamos_por_autor.c.autor_id == Autor.id)
    )
    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = db.execute(
        consulta.order_by(Autor.nombre)
        .offset(paginacion.skip)
        .limit(paginacion.limit)
    ).mappings()
    items = [ReporteAutor(**row) for row in filas]
    return armar_pagina(items, total, paginacion)


def resumen_biblioteca(db: Session) -> ResumenBiblioteca:
    libros = select(func.count(Libro.id)).scalar_subquery()
    ejemplares = select(func.coalesce(func.sum(Libro.ejemplares), 0)).scalar_subquery()
    prestados = (
        select(func.count(Prestamo.id))
        .where(Prestamo.fecha_devolucion.is_(None))
        .scalar_subquery()
    )
    socios_activos = (
        select(func.count(Socio.id)).where(Socio.activo.is_(True)).scalar_subquery()
    )
    vencidos = (
        select(func.count(Prestamo.id))
        .where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < date.today(),
        )
        .scalar_subquery()
    )
    multas = select(
        func.coalesce(func.sum(Prestamo.multa), Decimal("0"))
    ).scalar_subquery()
    multas_pendientes_total = (
        select(func.coalesce(func.sum(Prestamo.multa), Decimal("0")))
        .where(Prestamo.multa > 0, Prestamo.multa_pagada.is_(False))
        .scalar_subquery()
    )
    consulta = select(
        libros.label("total_libros"),
        ejemplares.label("total_ejemplares"),
        prestados.label("total_prestados"),
        socios_activos.label("socios_activos"),
        vencidos.label("prestamos_vencidos"),
        multas.label("total_multas"),
        multas_pendientes_total.label("multas_pendientes"),
    )
    return ResumenBiblioteca(**db.execute(consulta).mappings().one())
