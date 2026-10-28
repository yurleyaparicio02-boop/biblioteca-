from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.database import SessionLocal

router = APIRouter(prefix="/health")

@router.get("", summary="Verificar salud del servicio")
def health_check():
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "error"}
        )