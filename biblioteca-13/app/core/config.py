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

    @model_validator(mode="after")
    def validar_cors_prod(self) -> "Settings":
        if self.environment == "prod" and "*" in self.cors_origins:
            raise ValueError("No se permite '*' en cors_origins en el entorno prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
