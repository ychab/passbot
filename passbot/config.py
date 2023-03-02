from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseSettings, EmailStr, PostgresDsn, validator

PROJECT_DIR: Path = Path(__file__).parent
BASE_DIR: Path = PROJECT_DIR.parent


class Settings(BaseSettings):

    PROJECT_DIR: Path = PROJECT_DIR
    BASE_DIR: Path = BASE_DIR

    # DB connector
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

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
    EMAILS_TO: dict[str, list[EmailStr]]

    LANGUAGE_CODE: str = 'en'

    PASSBOT_LOG_FILE_PATH: Optional[str]
    PASSBOT_LOG_FILE_MAX_BYTES: int = 1024 * 1024 * 5
    PASSBOT_LOG_FILE_BACKUP_COUNT: int = 5
    PASSBOT_LOG_LEVEL: str = 'INFO'
    PASSBOT_LOG_HANDLERS: list[str] = ['console']

    PASSBOT_DATE_LIMIT: datetime
    PASSBOT_FILTER_AREA_CODES: Optional[list[str]] = None
    PASSBOT_TIMEOUT_MIN: int = 5

    class Config:
        case_sensitive = True
        env_file = [BASE_DIR / '.env']
        env_file_encoding = 'utf-8'

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if isinstance(v, str):  # pragma: no cover
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        return bool(values.get("SMTP_HOST"))

    @validator("PASSBOT_DATE_LIMIT", pre=True)
    def get_date_limit(cls, v: str, values: dict[str, Any]) -> datetime:
        if isinstance(v, datetime):  # pragma: no cover
            return v

        return datetime.strptime(v, '%Y-%m-%d').replace(tzinfo=timezone.utc)
