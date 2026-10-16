from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./neurotrack.db"

    jwt_secret: str = Field(default="dev-only-change-me-dev-only-change-me", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12
    cookie_name: str = "nt_session"
    cookie_secure: bool = False

    cors_origins: list[str] = ["http://localhost:3000"]

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.jwt_secret.startswith("dev-only"):
        raise RuntimeError("Üretimde JWT_SECRET ortam değişkeni tanımlanmalıdır.")
    return settings
