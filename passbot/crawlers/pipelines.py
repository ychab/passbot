from __future__ import annotations

from datetime import datetime, timedelta

from scrapy import Item, Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from itemadapter import ItemAdapter

from passbot import crud
from passbot.config import settings
from passbot.db import SessionFactory
from passbot.utils import now, send_email


class ZipcodeFilterPipeline:

    def __init__(self, area_code: str):
        self.AREA_CODE: str = area_code

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> ZipcodeFilterPipeline:
        return cls(
            area_code=crawler.settings.get(
                'AREA_CODE',
                settings.PASSBOT_FILTER_AREA_CODE,
            ),
        )

    def process_item(self, item: Item, spider: Spider) -> Item:
        adapter: ItemAdapter = ItemAdapter(item)
        zipcode: str = adapter.get('zipcode')

        if not zipcode or len(zipcode) != 5 or not zipcode.startswith(self.AREA_CODE):
            raise DropItem(f'Skip item with zipcode {zipcode}')

        return item


class DateFilterPipeline:

    def __init__(self, date_limit: datetime):
        self.DATE_LIMIT: datetime = date_limit

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> DateFilterPipeline:
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
    def from_crawler(cls, crawler: Crawler) -> TimeoutFilterPipeline:
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
        succeed: bool = send_email(subject=subject, body_text=body_text, body_html=body_html)
        if not succeed:
            raise DropItem('Error sending email')

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
