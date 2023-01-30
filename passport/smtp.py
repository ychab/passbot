import os
import smtplib
import ssl
from email.message import EmailMessage


class SMTPServer:

    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_TLS = bool(eval(os.getenv('SMTP_TLS', 'False')))
    DEFAULT_EMAIL = os.getenv('DEFAULT_EMAIL')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

    def send_email(self, subject, body_text, body_html):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.DEFAULT_EMAIL
        msg['To'] = self.ADMIN_EMAIL
        msg.set_content(body_text)
        msg.add_alternative(body_html, subtype='html')

        smtp_context = ssl.create_default_context()

        if self.SMTP_TLS:  # TLS default port to 587
            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.starttls(context=smtp_context)
                server.login(self.SMTP_USER, self.SMTP_PASSWORD)
                server.send_message(msg)
        else:  # SSL (more secure), default to 465
            with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT, context=smtp_context) as server:
                server.login(self.SMTP_USER, self.SMTP_PASSWORD)
                server.send_message(msg)


smtp_server = SMTPServer()
