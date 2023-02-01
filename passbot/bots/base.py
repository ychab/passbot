import logging
import os
from datetime import datetime, timedelta

import requests

from passbot.databases import SessionLocal
from passbot.models import EmailHistory
from passbot.smtp import smtp_server

logger = logging.getLogger(__name__)


class Bot:
    NAME = None
    URL_API = None
    URL_HOMEPAGE = None

    PASSBOT_TIMEOUT_MIN = int(os.getenv('PASSBOT_TIMEOUT_MIN', 5))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.NAME, 'Name should be set by children'
        assert self.URL_API, 'URLS must be set by children'
        assert self.URL_HOMEPAGE, 'URL_HOMEPAGE must be set by children'

    def start(self):
        if self._timeout_exceed():
            logger.debug('Skip due to timeout still active')
            return

        response = requests.get(self.URL_API)
        if not response.ok:
            logger.error(f'KO {response.status_code} response for {self.NAME} with url {self.URL_API}')
            return

        content = response.json()
        if self.should_alert(content):
            self._send_email()
            logger.info(f'Match founded! Email send for {self.NAME}')
        else:
            logger.info(f'No data founded for {self.NAME}')

    def should_alert(self, content) -> bool:
        raise NotImplementedError()

    def _send_email(self):
        subject = f'Alerte passeport - {self.NAME}'
        body_text = f'\nMatch founded, check:\n{self.URL_HOMEPAGE}'
        body_html = f"""
        <html lang="en">
            <head></head>
            <body>
                <p>Match founded: <a href="{self.URL_HOMEPAGE}" target="_blank">check the link</a></p>
            </body>
        </html>
        """

        smtp_server.send_email(subject=subject, body_text=body_text, body_html=body_html)
        self._log_db()

    def _timeout_exceed(self):
        date_max = datetime.now() - timedelta(minutes=self.PASSBOT_TIMEOUT_MIN)

        with SessionLocal() as db:
            count = db.query(EmailHistory) \
                .filter(
                    EmailHistory.bot == self.NAME,
                    EmailHistory.created > date_max) \
                .count()

        return count > 0

    def _log_db(self):
        log = EmailHistory(bot=self.NAME, created=datetime.now())

        with SessionLocal.begin() as db:
            db.add(log)
