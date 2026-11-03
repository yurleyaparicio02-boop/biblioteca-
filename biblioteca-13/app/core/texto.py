"""Utilidades de texto para filtros de búsqueda."""

from urllib.parse import urlparse

ESQUEMAS_IMAGEN = {"https", "http"}


def url_segura(valor: str | None, permitir_vacio: bool = False) -> str | None:
    """Valida que el enlace de imagen sea una URL http(s) y la devuelve en https.

    Se usa para almacenar únicamente enlaces de Cloudinary, nunca archivos.
    """
    if valor is None:
        return None
    limpio = valor.strip()
    if not limpio:
        return None if permitir_vacio else ""
    partes = urlparse(limpio)
    if partes.scheme not in ESQUEMAS_IMAGEN or not partes.netloc:
        raise ValueError("imagen_url debe ser una URL válida (https://...)")
    if partes.scheme == "http":
        return limpio.replace("http://", "https://", 1)
    return limpio


def patron_busqueda(texto: str | None) -> str | None:
    """Convierte un texto libre en un patrón LIKE/LIKE seguro.

    Escapa los comodines ``%`` y ``_`` (y el propio ``\\``) para que se
    busquen de forma literal, y devuelve el patrón listo para usar con
    ``columna.ilike(patron, escape="\\")``.
    """
    if texto is None:
        return None
    limpio = texto.strip()
    if not limpio:
        return None
    escapado = (
        limpio.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    )
    return f"%{escapado}%"
