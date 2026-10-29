import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from .core.config import get_settings
from .core.exceptions import ErrorAplicacion
from .core.security import limiter
from .routes import (
    auth,
    autores,
    categorias,
    health,
    libros,
    prestamos,
    reportes,
    socios,
    usuario,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("biblioteca")

settings = get_settings()

app = FastAPI(
    title="API de Biblioteca",
    description="Gestión integral de biblioteca con PostgreSQL, JWT, roles y FastAPI",
    version="2.0.0",
    docs_url=None if settings.environment == "prod" else "/docs",
    redoc_url=None if settings.environment == "prod" else "/redoc",
)

app.state.limiter = limiter

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def middleware_request_id_y_logs(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    inicio = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duracion_ms = (time.perf_counter() - inicio) * 1000
        logger.exception(
            "request_id=%s method=%s path=%s status=500 duration_ms=%.2f error=%s",
            request_id,
            request.method,
            request.url.path,
            duracion_ms,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"},
            headers={"X-Request-ID": request_id},
        )

    duracion_ms = (time.perf_counter() - inicio) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
    )
    return response


@app.get("/", tags=["Inicio"], summary="Página de entrada de la API")
def raiz() -> dict[str, str]:
    """Página de entrada con enlaces a la documentación y al resumen."""
    return {
        "mensaje": "API de Biblioteca en funcionamiento",
        "documentacion": "/docs",
        "openapi": "/openapi.json",
        "salud": "/api/v1/health",
        "resumen": "/api/v1/reportes/resumen",
    }


@app.exception_handler(RateLimitExceeded)
async def manejar_rate_limit(
    _: Request, __: RateLimitExceeded
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Se superó el límite de peticiones por minuto"},
    )


@app.exception_handler(ErrorAplicacion)
async def manejar_error_aplicacion(
    _: Request, error: ErrorAplicacion
) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.mensaje},
        headers=headers,
    )


@app.exception_handler(IntegrityError)
async def manejar_error_integridad(
    _: Request, __: IntegrityError
) -> JSONResponse:
    """Traduce violaciones de restricciones a 409 en lugar de un 500."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "La operación entra en conflicto con datos existentes "
                "(valor duplicado o referencia inválida)"
            )
        },
    )


@app.exception_handler(Exception)
async def manejar_error_interno(
    request: Request, error: Exception
) -> JSONResponse:
    logger.exception(
        "Error interno no controlado en %s %s: %s",
        request.method,
        request.url.path,
        type(error).__name__,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


# Inclusión de routers con el prefijo obligatorio /api/v1
app.include_router(health.router, prefix="/api/v1", tags=["Salud"])
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(usuario.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(autores.router, prefix="/api/v1", tags=["Autores"])
app.include_router(categorias.router, prefix="/api/v1", tags=["Categorías"])
app.include_router(libros.router, prefix="/api/v1", tags=["Libros"])
app.include_router(socios.router, prefix="/api/v1", tags=["Socios"])
app.include_router(prestamos.router, prefix="/api/v1", tags=["Préstamos"])
app.include_router(reportes.router, prefix="/api/v1", tags=["Reportes"])
