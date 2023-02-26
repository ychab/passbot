from typing import cast

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from passbot import settings

if not settings.SQLALCHEMY_DATABASE_URI:  # pragma: no cover
    raise RuntimeError('Did you forgot to configure DB?')

db_url: str = cast(str, settings.SQLALCHEMY_DATABASE_URI)
engine: Engine = create_engine(url=db_url)

SessionFactory: sessionmaker = sessionmaker(bind=engine)
SessionScoped: scoped_session = scoped_session(SessionFactory)
