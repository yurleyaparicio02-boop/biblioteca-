from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.dependencies import SessionDep

router = APIRouter(
    prefix="/health",
    tags=["Salud"],
    responses={503: {"description": "La base de datos no responde"}},
)


@router.get("", summary="Verificar salud del servicio y base de datos")
def health_check(db: SessionDep):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "error"},
        )
