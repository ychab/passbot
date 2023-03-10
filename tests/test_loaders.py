from datetime import datetime

import pytest
from scrapy import Spider
from scrapy.crawler import Crawler

from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.loaders import EmailHistoryLoader
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

crawler: Crawler = Crawler(
    spidercls=ViteMonPasseport44Spider,
    settings={
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
    },
)
spider: Spider = ViteMonPasseport44Spider.from_crawler(crawler)


def test_zipcode():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.add_value('zipcode', '(44000)')

    item = loader.load_item()
    assert item['zipcode'] == '44000'


def test_date_context_none():
    loader = EmailHistoryLoader(item=EmailHistoryItem())

    with pytest.raises(Exception) as exc:
        loader.add_value('date_slot', '15/06/2023 à 15:00')

    assert 'Missing context "datetime_format" and/or "date_format"' in str(exc.value)


def test_date_slot_month():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['datetime_format'] = spider.settings.get('DATETIME_FORMAT')
    loader.context['date_format'] = spider.settings.get('DATE_FORMAT')

    loader.add_value('date_slot', '6 mois')

    item = loader.load_item()
    assert item['date_slot']
    assert isinstance(item['date_slot'], datetime)


def test_date_slot_outdated():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['datetime_format'] = spider.settings.get('DATETIME_FORMAT')
    loader.context['date_format'] = spider.settings.get('DATE_FORMAT')

    loader.add_value('date_slot', 'Plus de 6 mois')

    item = loader.load_item()
    assert not item.get('date_slot')


def test_date_slot_datetime():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['datetime_format'] = spider.settings.get('DATETIME_FORMAT')
    loader.context['date_format'] = spider.settings.get('DATE_FORMAT')

    loader.add_value('date_slot', '15/06/2023 à 15:00')

    item = loader.load_item()
    assert isinstance(item['date_slot'], datetime)
    assert item['date_slot'].strftime('%Y-%m-%d %H:%M') == datetime(2023, 6, 15, 15, 0).strftime('%Y-%m-%d %H:%M')


def test_date_slot_date():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['datetime_format'] = spider.settings.get('DATETIME_FORMAT')
    loader.context['date_format'] = spider.settings.get('DATE_FORMAT')

    loader.add_value('date_slot', '15/06/2023')

    item = loader.load_item()
    assert isinstance(item['date_slot'], datetime)
    assert item['date_slot'].strftime('%Y-%m-%d') == datetime(2023, 6, 15).strftime('%Y-%m-%d')


def test_link_absolute():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['base_url'] = 'https://foo.com'
    loader.add_value('link', 'https://foo.com/bar')

    item = loader.load_item()
    assert item['link'] == 'https://foo.com/bar'


def test_link_relative():
    loader = EmailHistoryLoader(item=EmailHistoryItem())
    loader.context['base_url'] = 'https://foo.com'

    loader.add_value('link', '/bar')

    item = loader.load_item()
    assert item['link'] == 'https://foo.com/bar'
