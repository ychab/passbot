from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from passbot.models import EmailHistory


def history_create(db: Session, **fields: Any) -> EmailHistory:
    obj = EmailHistory(**fields)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def history_get(db: Session, spider: str, place: str, date_slot: datetime) -> Optional[EmailHistory]:
    stmt = select(EmailHistory).where(
        EmailHistory.spider == spider,
        EmailHistory.place == place,
        EmailHistory.date_slot == date_slot
    )
    return db.execute(stmt).scalar_one_or_none()


def history_timeout(
        db: Session,
        spider: str,
        zipcode: str,
        place: str,
        date_release: datetime,
) -> bool:

    stmt = select(EmailHistory).where(
        EmailHistory.spider == spider,
        EmailHistory.zipcode == zipcode,
        EmailHistory.place == place,
        EmailHistory.created > date_release,
    )

    return bool(db.execute(stmt).scalar_one_or_none())
