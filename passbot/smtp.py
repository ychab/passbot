import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from pydantic import EmailStr

from passbot.config import settings

logger = logging.getLogger(__name__)


class SMTPServer:

    def __init__(self) -> None:
        self.SMTP_HOST: str = settings.SMTP_HOST
        self.SMTP_PORT: int = settings.SMTP_PORT
        self.SMTP_USER: str = settings.SMTP_USER
        self.SMTP_PASSWORD: str = settings.SMTP_PASSWORD
        self.SMTP_AUTH: bool = settings.SMTP_AUTH
        self.SMTP_TLS: bool = settings.SMTP_TLS
        self.SMTP_SSL: bool = settings.SMTP_SSL
        self.SMTP_SSL_CONTEXT: bool = settings.SMTP_SSL_CONTEXT

        self.EMAILS_FROM: EmailStr = settings.EMAILS_FROM

    def send_email(
            self,
            recipients: list[EmailStr],
            subject: str,
            body_text: str,
            body_html: Optional[str] = None
    ) -> bool:

        msg: EmailMessage = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = self.EMAILS_FROM
        msg['To'] = ", ".join(recipients)

        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype='html')

        smtp_context: Optional[ssl.SSLContext] = None
        if self.SMTP_SSL_CONTEXT:
            smtp_context = ssl.create_default_context()

        try:
            if self.SMTP_SSL:
                with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT, context=smtp_context) as server:
                    if self.SMTP_AUTH:
                        server.login(self.SMTP_USER, self.SMTP_PASSWORD)
                    server.send_message(msg)

            else:
                with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                    if self.SMTP_TLS:
                        server.starttls(context=smtp_context)
                    if self.SMTP_AUTH:
                        server.login(self.SMTP_USER, self.SMTP_PASSWORD)
                    server.send_message(msg)

        except smtplib.SMTPException as exc:
            logger.exception(exc)
            return False
        else:
            # Just confirm it is send, NOT it is receive!
            return True


smtp_server = SMTPServer()
