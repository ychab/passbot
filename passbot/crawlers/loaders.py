from datetime import datetime, timedelta
from typing import Mapping, Optional
from urllib.parse import urlparse

from scrapy.loader import ItemLoader

from itemloaders.processors import MapCompose, TakeFirst
from slugify import slugify
from w3lib.html import remove_tags

from passbot.utils import now


def extract_zipcode(value: str) -> str:
    return value[1:-1]


def extract_date_slot(value: str, loader_context: Mapping) -> Optional[datetime]:
    datetime_format: str = loader_context.get('datetime_format', '')
    date_format: str = loader_context.get('date_format', '')

    if value.lower() in ['plus de 6 mois']:
        return None

    elif 'mois' in value.lower():
        month: int = int(value.split(' ')[0])
        return now() + timedelta(days=30 * month)

    else:
        if not datetime_format or not date_format:
            raise Exception('Missing context "datetime_format" and/or "date_format"')

        try:
            return datetime.strptime(value, datetime_format)
        except ValueError:
            date_only: str = value.split(' ')[0]
            return datetime.strptime(date_only, date_format)


def extract_link(value: str, loader_context: Mapping) -> str:
    prefix: str = ""
    if not urlparse(value).netloc:
        prefix = loader_context.get('base_url', '')
    return f"{prefix}{value}"


class EmailHistoryLoader(ItemLoader):

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    place_in = MapCompose(str.strip, remove_tags, slugify)
    zipcode_in = MapCompose(str.strip, extract_zipcode)
    date_slot_in = MapCompose(str.strip, extract_date_slot)
    link_in = MapCompose(str.strip, extract_link)
