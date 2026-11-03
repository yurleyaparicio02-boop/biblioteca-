from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    test_database_url: str | None = None
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = []
    environment: Literal["dev", "test", "prod"] = "dev"

    # Cloudinary: solo se guarda la secure_url del libro en la base de datos.
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None
    cloudinary_folder: str = "biblioteca/libros"
    # Se usa cuando un libro no tiene imagen registrada.
    imagen_libro_predeterminada: str = (
        "https://res.cloudinary.com/demo/image/upload/w_300,h_450,c_fill/sample.jpg"
    )

    @model_validator(mode="before")
    @classmethod
    def normalizar_url_postgres(cls, data: object) -> object:
        """Adapta la URL que entregan Render/Railway (postgres:// o postgresql://) al driver psycopg 3."""
        if isinstance(data, dict):
            for clave in ("database_url", "DATABASE_URL", "test_database_url", "TEST_DATABASE_URL"):
                url = data.get(clave)
                if isinstance(url, str):
                    if url.startswith("postgres://"):
                        data[clave] = url.replace("postgres://", "postgresql+psycopg://", 1)
                    elif url.startswith("postgresql://"):
                        data[clave] = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return data

    @model_validator(mode="after")
    def validar_cors_prod(self) -> "Settings":
        if self.environment == "prod" and "*" in self.cors_origins:
            raise ValueError("No se permite '*' en cors_origins en el entorno prod")
        return self

    @property
    def es_produccion(self) -> bool:
        return self.environment == "prod"

    @property
    def cloudinary_configurado(self) -> bool:
        return all(
            (
                self.cloudinary_cloud_name,
                self.cloudinary_api_key,
                self.cloudinary_api_secret,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
