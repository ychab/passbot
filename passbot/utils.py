from datetime import datetime, timezone
from typing import Optional

from passbot.smtp import smtp_server


def send_email(subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
    return smtp_server.send_email(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
    )


def now() -> datetime:
    return datetime.now(timezone.utc)
