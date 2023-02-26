from datetime import datetime

import pytest
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import DateFilterPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

crawler: Crawler = Crawler(
    spidercls=ViteMonPasseport44Spider,
    settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'DATE_LIMIT': settings.PASSBOT_FILTER_AREA_CODE,
    },
)
pipeline = DateFilterPipeline.from_crawler(crawler)
spider: Spider = ViteMonPasseport44Spider.from_crawler(crawler)


def test_date_missing():
    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=EmailHistoryItem(date_slot=None),
            spider=spider,
        )
    assert 'Skip item because no date founded' in str(exc.value)


def test_date_too_late():
    pipeline = DateFilterPipeline(date_limit=datetime(2023, 2, 12, 15, 12))

    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=EmailHistoryItem(date_slot=datetime(2023, 3, 12, 15, 12)),
            spider=spider,
        )
    assert 'Skip item because datetime is too late' in str(exc.value)


def test_date_valid():
    pipeline = DateFilterPipeline(date_limit=datetime(2023, 2, 12, 15, 12))
    dt = datetime(2023, 1, 12, 15, 12)

    item = pipeline.process_item(
        item=EmailHistoryItem(date_slot=dt),
        spider=spider,
    )
    assert item['date_slot'] == dt
