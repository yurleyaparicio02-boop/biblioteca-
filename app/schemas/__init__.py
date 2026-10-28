"""Esquemas de validación y respuesta de la API."""

from .autores import AutorActualizar, AutorCrear, AutorResponse, AutorResumen
from .categorias import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaResponse,
    CategoriaResumen,
)
from .libros import FiltroLibros, LibroActualizar, LibroCrear, LibroResponse
from .prestamos import (
    DevolucionCrear,
    EstadoMulta,
    EstadoPrestamo,
    PrestamoCrear,
    PrestamoDetalle,
    PrestamoResponse,
)
from .socios import SocioActualizar, SocioCrear, SocioResponse, SocioResumen

__all__ = [
    "AutorActualizar",
    "AutorCrear",
    "AutorResponse",
    "AutorResumen",
    "CategoriaActualizar",
    "CategoriaCrear",
    "CategoriaResponse",
    "CategoriaResumen",
    "DevolucionCrear",
    "EstadoMulta",
    "EstadoPrestamo",
    "FiltroLibros",
    "LibroActualizar",
    "LibroCrear",
    "LibroResponse",
    "PrestamoCrear",
    "PrestamoDetalle",
    "PrestamoResponse",
    "SocioActualizar",
    "SocioCrear",
    "SocioResponse",
    "SocioResumen",
]
