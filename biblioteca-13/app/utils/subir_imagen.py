import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from ..core.config import get_settings
from ..core.exceptions import ReglaNegocio, ServicioNoDisponible


def subir_bytes_cloudinary(
    archivo_bytes: bytes, content_type: str | None
) -> tuple[str, str | None]:
    """Valida y sube los bytes de una imagen a Cloudinary, retornando (secure_url, public_id)."""
    settings = get_settings()
    if not settings.cloudinary_configurado:
        raise ServicioNoDisponible(
            "Cloudinary no está configurado en las variables de entorno"
        )

    if not content_type or not content_type.startswith("image/"):
        raise ReglaNegocio("El archivo proporcionado no es una imagen válida")

    if not archivo_bytes:
        raise ReglaNegocio("El archivo de imagen está vacío")

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    try:
        resultado = cloudinary.uploader.upload(
            archivo_bytes,
            folder=settings.cloudinary_folder,
            resource_type="image",
        )
    except Exception as exc:
        raise ServicioNoDisponible(
            f"Error al subir la imagen a Cloudinary: {exc}"
        ) from exc

    secure_url = resultado.get("secure_url")
    if not secure_url:
        raise ServicioNoDisponible("Cloudinary no devolvió una URL segura")

    return str(secure_url), resultado.get("public_id")


async def subir_imagen_cloudinary(archivo: UploadFile) -> str:
    """Recibe un UploadFile de FastAPI, lo sube a Cloudinary y retorna la secure_url."""
    contenido = await archivo.read()
    secure_url, _ = subir_bytes_cloudinary(contenido, archivo.content_type)
    return secure_url
