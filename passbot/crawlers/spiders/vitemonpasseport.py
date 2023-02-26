from typing import Any, Generator, Optional
from urllib import parse
from urllib.parse import ParseResult

import scrapy
from scrapy import Selector
from scrapy.http import HtmlResponse

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.loaders import EmailHistoryLoader


class ViteMonPasseportSpider(scrapy.Spider):

    custom_settings: dict = {
        'TIMEOUT_MIN': settings.PASSBOT_TIMEOUT_MIN,
        'DATETIME_FORMAT': '%d/%m/%Y à %H:%M',
        'DATE_FORMAT': '%d/%m/%Y',
    }

    def parse(self, response: HtmlResponse, **kwargs: Any) -> Optional[Generator]:
        parsed_url: ParseResult = parse.urlparse(response.url)
        params: dict = parse.parse_qs(parsed_url.query)
        current_page: int = int(params.get('p', ['1'])[0])

        # Then treat each items of the list
        base_url: str = f'{parsed_url.scheme}://{parsed_url.hostname}'
        for node in response.xpath('//div[@id="search-list"]/section'):
            yield self.parse_item(node, response, base_url)

        # Finally, go to the next page if any
        next_link: str = response.xpath(f'//div[@class="pagination"]//a[@href="?p={current_page + 1}"]/@href').get()
        if next_link is not None:
            yield response.follow(next_link, self.parse)

    def parse_item(self, node: Selector, response: HtmlResponse, base_url: str) -> EmailHistoryItem:
        loader = EmailHistoryLoader(
            item=EmailHistoryItem(),
            selector=node,
            response=response,
        )

        loader.context['base_url'] = base_url
        loader.context['datetime_format'] = self.settings.get('DATETIME_FORMAT')
        loader.context['date_format'] = self.settings.get('DATE_FORMAT')

        loader.add_value('spider', self.name)
        loader.add_xpath('place', './/h2/text()')
        loader.add_xpath('zipcode', './/span[@class="zip"]/text()')
        loader.add_xpath('date_slot', './/div[contains(@class, "dispo")]/strong/text()')
        loader.add_xpath('link', './/div[contains(@class, "action")]/a/@href')

        return loader.load_item()


class ViteMonPasseport44Spider(ViteMonPasseportSpider):
    name: str = 'vitemonpasseport_44'

    start_urls: list[str] = [
        'https://www.vitemonpasseport.fr/ville/rdv-passeport-nantes-44000',
    ]
