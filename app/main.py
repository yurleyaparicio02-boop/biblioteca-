from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .core.config import get_settings
from .core.exceptions import ErrorAplicacion
from .routes import autores, categorias, health, libros, prestamos, reportes, socios

settings = get_settings()

app = FastAPI(
    title="API de Biblioteca",
    description="Gestión integral de biblioteca con PostgreSQL y FastAPI",
    version="3.0",
    docs_url=None if settings.environment == "prod" else "/docs",
    redoc_url=None if settings.environment == "prod" else "/redoc",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Inicio"])
def raiz() -> dict[str, str]:
    """Página de entrada con enlaces a la documentación y al resumen."""
    return {
        "mensaje": "API de Biblioteca en funcionamiento",
        "documentacion": "/docs",
        "openapi": "/openapi.json",
        "salud": "/api/v1/health",
        "resumen": "/api/v1/reportes/resumen",
    }


@app.exception_handler(ErrorAplicacion)
async def manejar_error_aplicacion(
    _: Request, error: ErrorAplicacion
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.mensaje},
    )


@app.exception_handler(IntegrityError)
async def manejar_error_integridad(
    _: Request, error: IntegrityError
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


# Inclusión de routers con el prefijo obligatorio /api/v1
app.include_router(health.router, prefix="/api/v1/health", tags=["Salud"])
app.include_router(autores.router, prefix="/api/v1/autores", tags=["Autores"])
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["Categorías"])
app.include_router(libros.router, prefix="/api/v1/libros", tags=["Libros"])
app.include_router(socios.router, prefix="/api/v1/socios", tags=["Socios"])
app.include_router(prestamos.router, prefix="/api/v1/prestamos", tags=["Préstamos"])
app.include_router(reportes.router, prefix="/api/v1/reportes", tags=["Reportes"])