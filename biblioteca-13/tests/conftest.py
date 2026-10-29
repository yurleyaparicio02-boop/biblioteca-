from collections.abc import Generator
from pathlib import Path
import sys
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module="starlette.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="starlette.*")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.core.security import limiter
from app.main import app


def _crear_engine_pruebas():
    settings = get_settings()
    test_url = settings.test_database_url
    if test_url:
        try:
            url_obj = make_url(test_url)
            db_name = url_obj.database
            admin_url = url_obj.set(database="postgres")
            admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
            with admin_engine.connect() as conn:
                existe = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": db_name},
                ).scalar()
                if not existe:
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            admin_engine.dispose()

            engine = create_engine(test_url, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception:
            pass

    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


engine_test = _crear_engine_pruebas()
TestingSessionLocal = sessionmaker(
    autoflush=False, expire_on_commit=False, bind=engine_test
)


@pytest.fixture(autouse=True)
def reiniciar_rate_limiter():
    """Reinicia el contador de slowapi antes de cada prueba."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="session", autouse=True)
def preparar_esquema():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

