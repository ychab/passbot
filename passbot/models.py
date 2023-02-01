from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EmailHistory(Base):

    __tablename__ = 'email_history'

    id = Column(Integer, primary_key=True, unique=True)
    bot = Column(String)
    created = Column(DateTime(timezone=True), server_default=func.now())
