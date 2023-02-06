from typing import Any, Generator, Optional

import scrapy
from scrapy.http import HtmlResponse

from passbot.crawlers.items import EmailHistoryItem


class SaintHerblainHotelSpider(scrapy.Spider):

    name: str = 'saintherblainhotel'

    start_urls: list[str] = [
        f'https://www.clicrdv.com/api/v2/availabletimeslots?group_id=155113&promotions=0&appointments[0][intervention_id]=2724111&appointments[0][calendar_id]=338429&apikey=71a07e028193455a8b8fa1c7da526291'  # noqa
    ]

    def parse(self, response: HtmlResponse, **kwargs: Any) -> Optional[Generator]:
        content: dict = response.json()
        if content.get('availabletimeslots'):

            yield EmailHistoryItem(
                spider=self.name,
                place='Saint Herblain Hotel de ville',
                zipcode='44800',
                date_slot=None,
                link='https://www.saint-herblain.fr/services-et-demarches/etat-civil-papiers-didentite-elections/carte-didentite-passeport',  # noqa
                extra_data={
                    'availabletimeslots': content.get('availabletimeslots'),
                },
            )
