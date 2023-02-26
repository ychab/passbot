from datetime import datetime, timezone
from unittest import mock

import pytest
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import SQLAlchemyError

from passbot import crud
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import SaveHistoryPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider
from passbot.models import EmailHistory

pipeline = SaveHistoryPipeline()
spider: Spider = ViteMonPasseport44Spider()


@mock.patch('passbot.crawlers.pipelines.crud')
def test_create_exception(mock_crud, session_db):
    mock_crud.history_create.side_effect = SQLAlchemyError('Boom')

    item = EmailHistoryItem(
        spider=spider.name,
        place='10 rue de la mairie',
        zipcode='44000',
        date_slot=datetime(2023, 1, 12, 15, 12, tzinfo=timezone.utc),
        link='https://foo.example.com',
        extra_data={'foo': 'bar'},
    )

    pipeline.open_spider(spider=spider)
    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=item,
            spider=spider,
        )
    pipeline.close_spider(spider=spider)

    assert 'DB error occured with' in str(exc.value)

    db_history: EmailHistory = crud.history_get(
        db=session_db,
        spider=spider.name,
        place=item['place'],
        date_slot=item['date_slot'],
    )
    assert not db_history


def test_create(session_db):
    item = EmailHistoryItem(
        spider=spider.name,
        place='10 rue de la mairie',
        zipcode='44000',
        date_slot=datetime(2023, 1, 12, 15, 12, tzinfo=timezone.utc),
        link='https://foo.example.com',
        extra_data={'foo': 'bar'},
        recipients=["foo@example.com", "bar@example.com"],
    )

    pipeline.open_spider(spider=spider)
    item = pipeline.process_item(
        item=item,
        spider=spider,
    )
    pipeline.close_spider(spider=spider)

    db_history: EmailHistory = crud.history_get(
        db=session_db,
        spider=spider.name,
        place=item['place'],
        date_slot=item['date_slot'],
    )
    assert db_history

    # Then check fields
    assert db_history.spider == item['spider']
    assert db_history.place == item['place']
    assert db_history.zipcode == item['zipcode']
    assert db_history.date_slot == item['date_slot']
    assert db_history.link == item['link']
    assert db_history.extra_data['foo'] == 'bar'
    assert len(db_history.recipients) > 0
    assert isinstance(db_history.created, datetime)
