from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from .autores import AutorResumen
from .socios import SocioResumen


class LibroMasPrestado(BaseModel):
    libro_id: int
    titulo: str
    autor: str
    total_prestamos: int


class LibrosPorCategoria(BaseModel):
    categoria_id: int
    categoria: str
    total_libros: int


class PrestamoVencidoReporte(BaseModel):
    prestamo_id: int
    titulo: str
    socio: str
    email: str
    fecha_limite: date
    dias_retraso: int


class SocioMultas(BaseModel):
    socio_id: int
    socio: str
    total_multas: Decimal
    prestamos_con_multa: int


class ReporteAutor(BaseModel):
    autor_id: int
    autor: str
    total_libros: int
    total_ejemplares: int
    total_prestamos: int


class ResumenBiblioteca(BaseModel):
    total_libros: int
    total_ejemplares: int
    total_prestados: int
    socios_activos: int
    prestamos_vencidos: int
    total_multas: Decimal
    multas_pendientes: Decimal
