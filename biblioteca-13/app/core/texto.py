"""Utilidades de texto para filtros de búsqueda."""


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
