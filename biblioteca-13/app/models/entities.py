from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column("libro_id", ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "categoria_id",
        ForeignKey("categorias.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nacionalidad: Mapped[str | None] = mapped_column(String(60))
    anio_nacimiento: Mapped[int | None] = mapped_column(Integer)
    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(200))
    libros: Mapped[list["Libro"]] = relationship(
        secondary=libro_categoria, back_populates="categorias"
    )


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    isbn: Mapped[str] = mapped_column(
        String(13), unique=True, index=True, nullable=False
    )
    anio_publicacion: Mapped[int] = mapped_column(Integer, nullable=False)
    ejemplares: Mapped[int] = mapped_column(Integer, nullable=False)
    autor_id: Mapped[int] = mapped_column(
        ForeignKey("autores.id"), index=True, nullable=False
    )

    autor: Mapped["Autor"] = relationship(back_populates="libros")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary=libro_categoria, back_populates="libros"
    )
    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="libro")


class Socio(Base):
    __tablename__ = "socios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(15))
    activo: Mapped[bool] = mapped_column(default=True, nullable=False)
    fecha_alta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="socio")


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id"), index=True, nullable=False
    )
    socio_id: Mapped[int] = mapped_column(
        ForeignKey("socios.id"), index=True, nullable=False
    )
    fecha_prestamo: Mapped[date] = mapped_column(
        Date, server_default=func.current_date(), nullable=False
    )
    fecha_limite: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date, index=True)
    multa: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    multa_pagada: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    registrado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), index=True, nullable=True
    )

    libro: Mapped["Libro"] = relationship(back_populates="prestamos")
    socio: Mapped["Socio"] = relationship(back_populates="prestamos")
