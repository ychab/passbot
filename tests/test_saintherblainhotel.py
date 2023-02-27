import json

from scrapy.http import TextResponse

from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.spiders.saintherblainhotel import SaintHerblainHotelPassportSpider


def test_parse_none():
    scrapy_response = TextResponse(
        SaintHerblainHotelPassportSpider.start_urls[0],
        body=json.dumps({}),
        encoding='utf-8',
    )

    spider = SaintHerblainHotelPassportSpider()
    items = list((spider.parse(scrapy_response)))
    assert len(items) == 0


def test_parse():
    scrapy_response = TextResponse(
        SaintHerblainHotelPassportSpider.start_urls[0],
        body=json.dumps({
            'availabletimeslots': {'first': 'now'},
        }),
        encoding='utf-8',
    )

    spider = SaintHerblainHotelPassportSpider()
    items = list((spider.parse(scrapy_response)))
    assert len(items) == 1

    item = items[0]
    assert isinstance(item, EmailHistoryItem)
    assert item['spider'] == spider.name
    assert item['place'] == 'Saint Herblain Hotel de ville'
    assert item['zipcode'] == '44800'
    assert item['link'] == 'https://www.saint-herblain.fr/services-et-demarches/etat-civil-papiers-didentite-elections/carte-didentite-passeport'  # noqa
    assert item['date_slot'] is None
    assert item['extra_data']['availabletimeslots']['first'] == 'now'
