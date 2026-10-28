import os
from collections.abc import Generator
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Configúrala en el entorno o en el archivo .env."
    )

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión por petición y la descarta al terminar.

    Si la petición falla a mitad de una transacción, el ``with`` cierra la
    sesión y el rollback implícito evita reutilizar una conexión en estado
    inconsistente.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def create_database_tables() -> None:
    from .. import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
