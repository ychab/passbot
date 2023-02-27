from typing import Any, Generator, Optional

import scrapy
from scrapy.http import HtmlResponse

from passbot.crawlers.items import EmailHistoryItem
from passbot.utils import now


class BaseSaintHerblainHotelSpider:

    name: str = 'saintherblainhotel'

    def parse(self, response: HtmlResponse, **kwargs: Any) -> Optional[Generator]:
        content: dict = response.json()
        if content.get('availabletimeslots'):

            yield EmailHistoryItem(
                spider=self.name,
                place='Saint Herblain Hotel de ville',
                zipcode='44800',
                date_slot=now(),
                link='https://www.saint-herblain.fr/services-et-demarches/etat-civil-papiers-didentite-elections/carte-didentite-passeport',  # noqa
                extra_data={
                    'availabletimeslots': content.get('availabletimeslots'),
                },
            )


class SaintHerblainHotelPassportSpider(BaseSaintHerblainHotelSpider, scrapy.Spider):

    name: str = 'saintherblainhotel_passport'

    start_urls: list[str] = [
        f'https://www.clicrdv.com/api/v2/availabletimeslots?group_id=155113&promotions=0&appointments[0][intervention_id]=2724111&appointments[0][calendar_id]=338429&apikey=71a07e028193455a8b8fa1c7da526291'  # noqa
    ]


class SaintHerblainHotelIdentitySpider(BaseSaintHerblainHotelSpider, scrapy.Spider):

    name: str = 'saintherblainhotel_identity'

    start_urls: list[str] = [
        f'https://www.clicrdv.com/api/v2/availabletimeslots?group_id=155113&promotions=0&appointments[0][intervention_id]=2724107&appointments[0][calendar_id]=338429&apikey=71a07e028193455a8b8fa1c7da526291',  # noqa
    ]
