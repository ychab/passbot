from datetime import datetime
from pathlib import Path

import pytest
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse

from slugify import slugify

from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

from tests import BASE_SAMPLES

crawler: Crawler = Crawler(
    spidercls=ViteMonPasseport44Spider,
    settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    },
)
spider: Spider = ViteMonPasseport44Spider.from_crawler(crawler)


def test_parse():
    content = (Path(BASE_SAMPLES) / 'vitemonpasseport' / 'p1.html').read_text()
    scrapy_response = HtmlResponse(
        ViteMonPasseport44Spider.start_urls[0],
        body=content,
        encoding='utf-8',
    )

    items = list((spider.parse(scrapy_response)))
    assert len(items) == 21

    item = items[0]
    assert isinstance(item, EmailHistoryItem)
    assert item['spider'] == spider.name
    assert item['place'] == slugify('Mairie de NANTES')
    assert item['zipcode'] == '44000'
    assert item['link'] == 'https://www.vitemonpasseport.fr/demande-passeport-mairie-de-nantes-44000'
    assert item['date_slot']

    item = items[1]
    assert item['date_slot'].strftime('%Y-%m-%d %H:%M') == datetime(2023, 4, 5, 15, 0).strftime('%Y-%m-%d %H:%M')


@pytest.mark.skip("@TODO")
def test_pagination():
    pass
