import json
from datetime import datetime

from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse

from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.spiders.check import CheckSpider


def test_parse():
    scrapy_response = HtmlResponse(
        CheckSpider.start_urls[0],
        body=json.dumps({}),
        encoding='utf-8',
    )

    crawler: Crawler = Crawler(CheckSpider, settings={
        'AREA_CODE': '44000',
        'DATE_LIMIT': datetime(2023, 2, 28, 15,)
    })
    spider = CheckSpider.from_crawler(crawler)

    items = list((spider.parse(scrapy_response)))
    assert len(items) == 1

    item = items[0]
    assert isinstance(item, EmailHistoryItem)
    assert item['spider'] == spider.name
    assert item['place'] == 'Scrapy website itself'
    assert item['zipcode'] == spider.settings.get('AREA_CODE')
    assert item['date_slot'] < spider.settings.get('DATE_LIMIT')
