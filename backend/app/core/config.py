from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str = "postgresql+asyncpg://joker:joker@localhost:5432/joker_auto_rent"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 30
    env: Literal["development", "production"] = "development"
    frontend_url: str = "http://localhost:5173"
    currency: str = "KZT"
    timezone: str = "Asia/Almaty"
    media_dir: str = "media"
    # Почта для кодов подтверждения. Пустой SMTP_HOST — письма пишутся в лог
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Joker Auto Rent <no-reply@joker.kz>"
    smtp_tls: bool = True
    email_code_ttl_min: int = 15
    email_resend_cooldown_sec: int = 60
    email_code_max_attempts: int = 5
    max_booking_days: int = 90

    @field_validator("database_url")
    @classmethod
    def _async_driver(cls, value: str) -> str:
        # Хостинги (Railway и др.) отдают postgresql:// — SQLAlchemy async нужен asyncpg
        for prefix in ("postgresql://", "postgres://"):
            if value.startswith(prefix):
                return "postgresql+asyncpg://" + value.removeprefix(prefix)
        return value

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @model_validator(mode="after")
    def _check_production(self) -> "Settings":
        if self.is_production and self.jwt_secret == "change-me":
            raise ValueError("JWT_SECRET must be set in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
