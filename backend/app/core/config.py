from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "ANNIE AI"
    app_env: str = "development"
    debug: bool = True

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "annie_db"
    database_user: str = "annie"
    database_password: str = "annie_password"

    database_url: str

    ai_api_key: str | None = None

    whatsapp_verify_token: str | None = None
    whatsapp_access_token: str | None = None
    whatsapp_phone_number_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
