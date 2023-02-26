import logging
from datetime import datetime
from unittest import mock

import pytest
from scrapy.exceptions import DropItem

from passbot import settings
from passbot.crawlers.items import EmailHistoryItem
from passbot.crawlers.pipelines import SendEmailHistoryPipeline
from passbot.crawlers.spiders.vitemonpasseport import ViteMonPasseport44Spider

pipeline = SendEmailHistoryPipeline()
spider = ViteMonPasseport44Spider()


@mock.patch('passbot.utils.smtp_server')
def test_send_email_exception(mock_smtp):
    mock_smtp.send_email.return_value = False

    item = EmailHistoryItem(
        spider=spider.name,
        zipcode='44000',
        date_slot=datetime(2023, 1, 12, 15, 12),
        link='https://foo.example.com',
    )

    with pytest.raises(DropItem) as exc:
        pipeline.process_item(
            item=item,
            spider=spider,
        )

    assert 'Error sending email' in str(exc.value)


def test_send_no_recipient(monkeypatch, caplog):
    monkeypatch.setattr(settings, 'EMAILS_TO', {spider.name: []})

    item = EmailHistoryItem(
        spider=spider.name,
        zipcode='44000',
        date_slot=datetime(2023, 1, 12, 15, 12),
        link='https://foo.example.com',
    )

    with caplog.at_level(level=logging.WARNING, logger='passbot.crawlers.pipelines'):
        pipeline.process_item(
            item=item,
            spider=spider,
        )

    assert 'detect alert but no email subscribed' in caplog.text


@mock.patch('passbot.utils.smtp_server')
def test_send_email(mock_smtp):
    mock_smtp.send_email.return_value = True

    item = EmailHistoryItem(
        spider=spider.name,
        zipcode='44000',
        date_slot=datetime(2023, 1, 12, 15, 12),
        link='https://foo.example.com',
    )

    item = pipeline.process_item(
        item=item,
        spider=spider,
    )
    assert item
    assert len(item['recipients']) > 0
