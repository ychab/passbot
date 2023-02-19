from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.exc import SQLAlchemyError

from passbot import crud
from passbot.config import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import (
    DateFilterPipeline, SaveHistoryPipeline, SendEmailHistoryPipeline, TimeoutFilterPipeline, ZipcodeFilterPipeline,
)
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider
from passbot.models import EmailHistory
from passbot.utils import now

from tests.utils.base import BaseTestCase
from tests.utils.factory import EmailHistoryFactory


class TestZipcodeFilterPipeline:

    @classmethod
    def setup_class(cls):
        cls.area_code: str = settings.PASSBOT_FILTER_AREA_CODE
        cls.pipeline = ZipcodeFilterPipeline(area_code=cls.area_code)
        cls.spider: Spider = ViteMonPasseport44Spider()

    def test_zipcode_valid(self):
        item = self.pipeline.process_item(
            item=EmailHistoryItem(zipcode='44000'),
            spider=self.spider,
        )
        assert item['zipcode'] == '44000'

    def test_zipcode_none(self):
        with pytest.raises(DropItem):
            self.pipeline.process_item(
                item=EmailHistoryItem(zipcode=None),
                spider=self.spider,
            )

    def test_zipcode_invalid_length(self):
        with pytest.raises(DropItem):
            self.pipeline.process_item(
                item=EmailHistoryItem(zipcode='448008'),
                spider=self.spider,
            )

    def test_zipcode_excluded(self):
        with pytest.raises(DropItem):
            self.pipeline.process_item(
                item=EmailHistoryItem(zipcode='98800'),
                spider=self.spider,
            )


class TestDateFilterPipeline:

    @classmethod
    def setup_class(cls):
        cls.date_limit: datetime = settings.PASSBOT_DATE_LIMIT
        cls.pipeline = DateFilterPipeline(date_limit=cls.date_limit)
        cls.spider: Spider = ViteMonPasseport44Spider()

    def test_date_missing(self):
        with pytest.raises(DropItem) as exc:
            self.pipeline.process_item(
                item=EmailHistoryItem(date_slot=None),
                spider=self.spider,
            )
        assert 'Skip item because no date founded' in str(exc.value)

    def test_date_too_late(self):
        pipeline = DateFilterPipeline(date_limit=datetime(2023, 2, 12, 15, 12))

        with pytest.raises(DropItem) as exc:
            pipeline.process_item(
                item=EmailHistoryItem(date_slot=datetime(2023, 3, 12, 15, 12)),
                spider=self.spider,
            )
        assert 'Skip item because datetime is too late' in str(exc.value)

    def test_date_valid(self):
        pipeline = DateFilterPipeline(date_limit=datetime(2023, 2, 12, 15, 12))
        dt = datetime(2023, 1, 12, 15, 12)

        item = pipeline.process_item(
            item=EmailHistoryItem(date_slot=dt),
            spider=self.spider,
        )
        assert item['date_slot'] == dt


class TestTimeoutFilterPipeline(BaseTestCase):

    @classmethod
    def setup_class(cls):
        cls.timeout_min: int = settings.PASSBOT_TIMEOUT_MIN
        cls.pipeline = TimeoutFilterPipeline(timeout_min=cls.timeout_min)
        cls.spider: Spider = ViteMonPasseport44Spider()

    @mock.patch('passbot.crawlers.pipelines.now')
    def test_locked(self, mock_now):
        mock_now.return_value = now() - timedelta(minutes=self.timeout_min - 1)

        entry: EmailHistory = EmailHistoryFactory()

        item = EmailHistoryItem(
            spider=entry.spider,
            zipcode=entry.zipcode,
            place=entry.place,
            date_slot=entry.date_slot,
        )

        self.pipeline.open_spider(spider=self.spider)
        with pytest.raises(DropItem) as exc:
            self.pipeline.process_item(
                item=item,
                spider=self.spider,
            )
        self.pipeline.close_spider(spider=self.spider)

        assert 'Skip timeout' in str(exc.value)

    @mock.patch('passbot.crawlers.pipelines.now')
    def test_locked_not_anymore(self, mock_now):
        mock_now.return_value = now() + timedelta(minutes=self.timeout_min + 1)

        entry: EmailHistory = EmailHistoryFactory()

        item = EmailHistoryItem(
            spider=entry.spider,
            zipcode=entry.zipcode,
            place=entry.place,
            date_slot=entry.date_slot,
        )

        self.pipeline.open_spider(spider=self.spider)
        item = self.pipeline.process_item(
            item=item,
            spider=self.spider,
        )
        self.pipeline.close_spider(spider=self.spider)

        assert item

    def test_locked_not(self):
        item = EmailHistoryItem(
            spider=self.spider.name,
            zipcode='44000',
            place='44 route de monsieur segin',
            date_slot=datetime(2023, 1, 12, 15, 12),
        )

        self.pipeline.open_spider(spider=self.spider)
        item = self.pipeline.process_item(
            item=item,
            spider=self.spider,
        )
        self.pipeline.close_spider(spider=self.spider)

        assert item


class TestSendEmailHistoryPipeline:

    @classmethod
    def setup_class(cls):
        cls.pipeline = SendEmailHistoryPipeline()
        cls.spider = ViteMonPasseport44Spider()

    @mock.patch('passbot.utils.smtp_server')
    def test_send_email_exception(self, mock_smtp):
        mock_smtp.send_email.return_value = False

        item = EmailHistoryItem(
            spider=self.spider.name,
            zipcode='44000',
            date_slot=datetime(2023, 1, 12, 15, 12),
            link='https://foo.example.com',
        )

        with pytest.raises(DropItem) as exc:
            self.pipeline.process_item(
                item=item,
                spider=self.spider,
            )

        assert 'Error sending email' in str(exc.value)

    @mock.patch('passbot.utils.smtp_server')
    def test_send_email(self, mock_smtp):
        mock_smtp.send_email.return_value = True

        item = EmailHistoryItem(
            spider=self.spider.name,
            zipcode='44000',
            date_slot=datetime(2023, 1, 12, 15, 12),
            link='https://foo.example.com',
        )

        item = self.pipeline.process_item(
            item=item,
            spider=self.spider,
        )
        assert item


class TestSaveHistoryPipeline(BaseTestCase):

    @classmethod
    def setup_class(cls):
        cls.pipeline = SaveHistoryPipeline()
        cls.spider: Spider = ViteMonPasseport44Spider()

    @mock.patch('passbot.crawlers.pipelines.crud')
    def test_create_exception(self, mock_crud):
        mock_crud.history_create.side_effect = SQLAlchemyError('Boom')

        item = EmailHistoryItem(
            spider=self.spider.name,
            place='10 rue de la mairie',
            zipcode='44000',
            date_slot=datetime(2023, 1, 12, 15, 12, tzinfo=timezone.utc),
            link='https://foo.example.com',
            extra_data={'foo': 'bar'},
        )

        self.pipeline.open_spider(spider=self.spider)
        with pytest.raises(DropItem) as exc:
            self.pipeline.process_item(
                item=item,
                spider=self.spider,
            )
        self.pipeline.close_spider(spider=self.spider)

        assert 'DB error occured with' in str(exc.value)

        db_history: EmailHistory = crud.history_get(
            db=self.db_session,
            spider=self.spider.name,
            place=item['place'],
            date_slot=item['date_slot'],
        )
        assert not db_history

    def test_create(self):
        item = EmailHistoryItem(
            spider=self.spider.name,
            place='10 rue de la mairie',
            zipcode='44000',
            date_slot=datetime(2023, 1, 12, 15, 12, tzinfo=timezone.utc),
            link='https://foo.example.com',
            extra_data={'foo': 'bar'},
        )

        self.pipeline.open_spider(spider=self.spider)
        item = self.pipeline.process_item(
            item=item,
            spider=self.spider,
        )
        self.pipeline.close_spider(spider=self.spider)

        db_history: EmailHistory = crud.history_get(
            db=self.db_session,
            spider=self.spider.name,
            place=item['place'],
            date_slot=item['date_slot'],
        )
        assert db_history

        # Then check fields
        assert db_history.spider == item['spider']
        assert db_history.place == item['place']
        assert db_history.zipcode == item['zipcode']
        assert db_history.date_slot == item['date_slot']
        assert db_history.link == item['link']
        assert db_history.extra_data['foo'] == 'bar'
        assert isinstance(db_history.created, datetime)
