import logging
from datetime import datetime, timedelta
from typing import Optional, Self

from scrapy import Item, Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from itemadapter import ItemAdapter

from passbot import crud, settings
from passbot.db import SessionFactory
from passbot.utils import get_recipients_for_spider, now, send_email

logger = logging.getLogger(__name__)


class ZipcodeFilterPipeline:

    def __init__(self, area_codes: Optional[list[str]] = None):
        self.AREA_CODES: Optional[list[str]] = area_codes

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(
            area_codes=crawler.settings.get(
                'AREA_CODES',
                settings.PASSBOT_FILTER_AREA_CODES,
            ),
        )

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter: ItemAdapter = ItemAdapter(item)
        zipcode: str = adapter.get('zipcode')

        if not zipcode or len(zipcode) != 5:
            raise DropItem('Skip item without zipcode or invalid')

        match = zipcode.startswith(tuple(self.AREA_CODES)) if self.AREA_CODES else True
        if not match:
            raise DropItem(f'Skip item with zipcode {zipcode} not matching {self.AREA_CODES}')

        return item


class DateFilterPipeline:

    def __init__(self, date_limit: datetime):
        self.DATE_LIMIT: datetime = date_limit

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(
            date_limit=crawler.settings.get(
                'DATE_LIMIT',
                settings.PASSBOT_DATE_LIMIT,
            ),
        )

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter: ItemAdapter = ItemAdapter(item)
        date_slot: datetime = adapter.get('date_slot')

        if not date_slot:
            raise DropItem('Skip item because no date founded (or too late)')

        elif date_slot > self.DATE_LIMIT:
            raise DropItem(f'Skip item because datetime is too late: {date_slot}')

        return item


class TimeoutFilterPipeline:

    def __init__(self, timeout_min: int):
        self.TIMEOUT_MIN: int = timeout_min

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(
            timeout_min=crawler.settings.get(
                'TIMEOUT_MIN',
                settings.PASSBOT_TIMEOUT_MIN,
            ),
        )

    def open_spider(self, spider: Spider) -> None:
        self.db: Session = SessionFactory()

    def close_spider(self, spider: Spider) -> None:
        self.db.close()

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter = ItemAdapter(item)

        is_timeout: bool = crud.history_timeout(
            db=self.db,
            spider=adapter['spider'],
            zipcode=adapter['zipcode'],
            place=adapter['place'],
            date_release=now() - timedelta(minutes=self.TIMEOUT_MIN),
        )

        if is_timeout:
            raise DropItem(
                f"Skip timeout item for spider {adapter['spider']} "
                f"with place: {adapter['place']} and date: {adapter['date_slot']}")

        return item


class SendEmailHistoryPipeline:

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter: ItemAdapter = ItemAdapter(item)

        subject: str = f'Alert detected by spider {spider.name}'
        body_text: str = f"""
        Spider {spider.name} detected a new alert:
        - zipcode {adapter.get('zipcode')}
        - date: {adapter.get('date_slot')}
        - link: {adapter.get('link')}
"""
        body_html = f"""
        <p>Spider {spider.name} detected a new alert:</p>
        <ul>
            <li>spider: {adapter.get('spider')}</li>
            <li>zipcode: {adapter.get('zipcode')}</li>
            <li>date: {adapter.get('date_slot')}</li>
            <li>link: <a href="{adapter.get('link')}" target="_blank">Click here</a></li>
        </ul>
"""
        recipients = get_recipients_for_spider(spider.name)
        if recipients:
            succeed: bool = send_email(
                recipients=recipients,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
            )
            if not succeed:
                raise DropItem('Error sending email')
        else:
            logger.warning(f"Spider {spider.name} detect alert but no email subscribed")

        # Even empty, store recipients.
        item['recipients'] = recipients
        return item


class SaveHistoryPipeline:

    def open_spider(self, spider: Spider) -> None:
        self.db: Session = SessionFactory()

    def close_spider(self, spider: Spider) -> None:
        self.db.close()

    def process_item(self, item: Item, spider: Spider) -> Item:
        try:
            crud.history_create(db=self.db, **ItemAdapter(item).asdict())
        except SQLAlchemyError as exc:
            raise DropItem(f'DB error occured with {exc}')
        else:
            return item
