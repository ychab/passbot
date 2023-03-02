import pytest
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import ZipcodeFilterPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider


@pytest.fixture
def crawler(request) -> Crawler:
    settings: dict = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'AREA_CODES': ["440", "441", "442", "443", "447", "448"],
    }
    if getattr(request, "param", None):
        settings.update(request.param)

    return Crawler(
        spidercls=ViteMonPasseport44Spider,
        settings=settings,
    )


@pytest.fixture
def pipeline(crawler: Crawler) -> ZipcodeFilterPipeline:
    return ZipcodeFilterPipeline.from_crawler(crawler)


@pytest.fixture
def spider(crawler: Crawler) -> ViteMonPasseport44Spider:
    return ViteMonPasseport44Spider.from_crawler(crawler)


@pytest.mark.parametrize('crawler', [{'AREA_CODES': None}], indirect=True)
def test_missing_conf(monkeypatch, crawler):
    monkeypatch.setattr(settings, "PASSBOT_FILTER_AREA_CODES", None)

    pipeline = ZipcodeFilterPipeline.from_crawler(crawler)
    spider = ViteMonPasseport44Spider.from_crawler(crawler)

    item = pipeline.process_item(
        item=EmailHistoryItem(zipcode='98456'),
        spider=spider,
    )
    assert item['zipcode'] == '98456'


@pytest.mark.parametrize('crawler', [{'AREA_CODES': []}], indirect=True)
def test_filter_empty(crawler):
    pipeline = ZipcodeFilterPipeline.from_crawler(crawler)
    spider = ViteMonPasseport44Spider.from_crawler(crawler)

    item = pipeline.process_item(
        item=EmailHistoryItem(zipcode='98456'),
        spider=spider,
    )
    assert item['zipcode'] == '98456'


def test_zipcode_none(pipeline, spider):
    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=EmailHistoryItem(zipcode=None),
            spider=spider,
        )
    assert str(exc.value) == "Skip item without zipcode or invalid"


def test_zipcode_invalid_length(pipeline, spider):
    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=EmailHistoryItem(zipcode='448008'),
            spider=spider,
        )
    assert str(exc.value) == "Skip item without zipcode or invalid"


def test_zipcode_excluded(pipeline, spider):
    with pytest.raises(DropItem):
        pipeline.process_item(
            item=EmailHistoryItem(zipcode='98800'),
            spider=spider,
        )


def test_zipcode_valid(pipeline, spider):
    item = pipeline.process_item(
        item=EmailHistoryItem(zipcode='44000'),
        spider=spider,
    )
    assert item['zipcode'] == '44000'
