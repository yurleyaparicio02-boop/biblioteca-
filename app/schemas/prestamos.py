from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .libros import LibroResumen
from .socios import SocioResumen


class EstadoPrestamo(str, Enum):
    activo = "activo"
    vencido = "vencido"
    devuelto = "devuelto"


class EstadoMulta(str, Enum):
    sin_multa = "sin_multa"
    pendiente = "pendiente"
    pagada = "pagada"


class PrestamoCrear(BaseModel):
    libro_id: int = Field(gt=0)
    socio_id: int = Field(gt=0)
    fecha_prestamo: date = Field(default_factory=date.today)
    dias: int = Field(default=14, ge=1, le=30)


class DevolucionCrear(BaseModel):
    fecha_devolucion: date = Field(default_factory=date.today)


class PrestamoResponse(BaseModel):
    id: int
    libro_id: int
    socio_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    multa: Decimal
    multa_pagada: bool
    estado_multa: EstadoMulta
    estado: EstadoPrestamo
    model_config = ConfigDict(from_attributes=True)


class PrestamoDetalle(PrestamoResponse):
    libro: LibroResumen
    socio: SocioResumen
