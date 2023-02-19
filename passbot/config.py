from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):

    # DB connector
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # SMTP connector
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_AUTH: bool = True
    SMTP_TLS: bool = False
    SMTP_SSL: bool = True
    SMTP_SSL_CONTEXT: bool = True

    EMAILS_ENABLED: bool = False
    EMAILS_FROM: EmailStr
    EMAILS_TO: EmailStr

    LANGUAGE_CODE: str = 'en'

    PASSBOT_LOG_PATH: str = '/tmp/passbot.log'
    PASSBOT_LOG_LEVEL: str = 'DEBUG'

    PASSBOT_DATE_LIMIT: datetime
    PASSBOT_FILTER_AREA_CODE: str
    PASSBOT_TIMEOUT_MIN: int = 5

    class Config:
        case_sensitive = True

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if isinstance(v, str):  # pragma: no cover
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        return bool(values.get("SMTP_HOST"))

    @validator("PASSBOT_DATE_LIMIT", pre=True)
    def get_date_limit(cls, v: str, values: dict[str, Any]) -> datetime:
        if isinstance(v, datetime):  # pragma: no cover
            return v

        return datetime.strptime(v, '%Y-%m-%d').replace(tzinfo=timezone.utc)


settings = Settings()
