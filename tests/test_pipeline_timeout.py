from datetime import timedelta, datetime
from unittest import mock

import pytest
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import TimeoutFilterPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider
from passbot.models import EmailHistory
from passbot.utils import now
from tests.utils.factory import EmailHistoryFactory

timeout_min = settings.PASSBOT_TIMEOUT_MIN

crawler: Crawler = Crawler(
    spidercls=ViteMonPasseport44Spider,
    settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'TIMEOUT_MIN': timeout_min,
    },
)
pipeline = TimeoutFilterPipeline.from_crawler(crawler)
spider: Spider = ViteMonPasseport44Spider.from_crawler(crawler)


@mock.patch('passbot.crawlers.pipelines.now')
def test_locked(mock_now, session_db):
    mock_now.return_value = now() - timedelta(minutes=timeout_min - 1)

    entry: EmailHistory = EmailHistoryFactory()

    item = EmailHistoryItem(
        spider=entry.spider,
        zipcode=entry.zipcode,
        place=entry.place,
        date_slot=entry.date_slot,
    )

    pipeline.open_spider(spider=spider)
    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=item,
            spider=spider,
        )
    pipeline.close_spider(spider=spider)

    assert 'Skip timeout' in str(exc.value)


@mock.patch('passbot.crawlers.pipelines.now')
def test_locked_not_anymore(mock_now, session_db):
    mock_now.return_value = now() + timedelta(minutes=timeout_min + 1)

    entry: EmailHistory = EmailHistoryFactory()

    item = EmailHistoryItem(
        spider=entry.spider,
        zipcode=entry.zipcode,
        place=entry.place,
        date_slot=entry.date_slot,
    )

    pipeline.open_spider(spider=spider)
    item = pipeline.process_item(
        item=item,
        spider=spider,
    )
    pipeline.close_spider(spider=spider)

    assert item


def test_locked_not(session_db):
    item = EmailHistoryItem(
        spider=spider.name,
        zipcode='44000',
        place='44 route de monsieur segin',
        date_slot=datetime(2023, 1, 12, 15, 12),
    )

    pipeline.open_spider(spider=spider)
    item = pipeline.process_item(
        item=item,
        spider=spider,
    )
    pipeline.close_spider(spider=spider)

    assert item
