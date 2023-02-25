from datetime import datetime, timezone

import factory
from factory import fuzzy

from passbot.config import settings
from passbot.db import SessionScoped
from passbot.models import EmailHistory


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        sqlalchemy_session = SessionScoped
        sqlalchemy_session_persistence = "commit"


class EmailHistoryFactory(BaseFactory):

    class Meta:
        model = EmailHistory

    spider = factory.Faker("word", locale=settings.LANGUAGE_CODE)
    place = factory.Faker("address", locale=settings.LANGUAGE_CODE)
    zipcode = factory.Faker("postcode", locale=settings.LANGUAGE_CODE)
    date_slot = fuzzy.FuzzyDateTime(datetime.now(tz=timezone.utc))
    link = factory.Faker("uri", locale=settings.LANGUAGE_CODE)
    recipients = factory.List([
        "foo@example.com",
        "bar@example.com",
    ])
