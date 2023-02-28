from datetime import timedelta
from typing import Any, Generator, Optional

import scrapy
from scrapy.http import HtmlResponse

from passbot.crawlers.items import EmailHistoryItem


class CheckSpider(scrapy.Spider):

    name: str = 'check'

    start_urls: list[str] = [
        'https://scrapy.org'
    ]

    def parse(self, response: HtmlResponse, **kwargs: Any) -> Optional[Generator]:
        yield EmailHistoryItem(
            spider=self.name,
            place='Scrapy website itself',
            zipcode=self.settings.get('AREA_CODE'),
            date_slot=self.settings.get('DATE_LIMIT') - timedelta(days=5),
        )
