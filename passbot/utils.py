from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr

from passbot import settings
from passbot.smtp import smtp_server


def send_email(
        recipients: list[EmailStr],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
) -> bool:

    return smtp_server.send_email(
        recipients=recipients,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
    )


def get_recipients_for_spider(spider: str) -> list[EmailStr]:
    recipients = settings.EMAILS_TO.get(spider, [])
    recipients += settings.EMAILS_TO.get('*', [])
    return recipients


def now() -> datetime:
    return datetime.now(timezone.utc)
