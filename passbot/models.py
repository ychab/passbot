from sqlalchemy import ARRAY, JSON, Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EmailHistory(Base):

    __tablename__ = 'email_history'

    id = Column(Integer, primary_key=True, unique=True)

    spider = Column(String(length=128))
    place = Column(String(length=128))
    zipcode = Column(String(length=32))
    date_slot = Column(DateTime(timezone=True))
    link = Column(String(length=2048))

    recipients = Column(ARRAY(String))
    extra_data = Column(JSON, nullable=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
