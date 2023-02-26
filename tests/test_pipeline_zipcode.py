import pytest
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import ZipcodeFilterPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

crawler: Crawler = Crawler(
    spidercls=ViteMonPasseport44Spider,
    settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'AREA_CODE': settings.PASSBOT_FILTER_AREA_CODE,
    },
)
pipeline = ZipcodeFilterPipeline.from_crawler(crawler)
spider: Spider = ViteMonPasseport44Spider.from_crawler(crawler)


def test_zipcode_valid():
    item = pipeline.process_item(
        item=EmailHistoryItem(zipcode='44000'),
        spider=spider,
    )
    assert item['zipcode'] == '44000'


def test_zipcode_none():
    with pytest.raises(DropItem):
        pipeline.process_item(
            item=EmailHistoryItem(zipcode=None),
            spider=spider,
        )


def test_zipcode_invalid_length():
    with pytest.raises(DropItem):
        pipeline.process_item(
            item=EmailHistoryItem(zipcode='448008'),
            spider=spider,
        )


def test_zipcode_excluded():
    with pytest.raises(DropItem):
        pipeline.process_item(
            item=EmailHistoryItem(zipcode='98800'),
            spider=spider,
        )
