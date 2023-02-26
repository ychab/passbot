import logging
import smtplib
from unittest import mock

from passbot.smtp import SMTPServer

EMAILS_TO = ['dummy@example.com']


@mock.patch('passbot.smtp.smtplib.SMTP')
@mock.patch('passbot.smtp.settings')
def test_html(mock_settings, mock_smtp):
    mock_settings.SMTP_SSL = False
    mock_settings.SMTP_SSL_CONTEXT = False
    mock_settings.SMTP_TLS = False
    mock_settings.SMTP_AUTH = False

    smtp_server = SMTPServer()
    succeed = smtp_server.send_email(
        recipients=EMAILS_TO,
        subject='foo',
        body_text='bla bla bla',
        body_html='<html><head></head><body><p>Hey!</p></body></html>',
    )
    assert succeed is True


@mock.patch('passbot.smtp.smtplib.SMTP')
@mock.patch('passbot.smtp.settings')
def test_tls_auth(mock_settings, mock_smtp):
    mock_settings.SMTP_SSL = False
    mock_settings.SMTP_SSL_CONTEXT = False
    mock_settings.SMTP_TLS = True
    mock_settings.SMTP_AUTH = True

    smtp_server = SMTPServer()
    succeed = smtp_server.send_email(EMAILS_TO, 'foo', 'bla bla bla')
    assert succeed is True


@mock.patch('passbot.smtp.smtplib.SMTP')
@mock.patch('passbot.smtp.settings')
def test_no_tls_auth(mock_settings, mock_smtp):
    mock_settings.SMTP_SSL = False
    mock_settings.SMTP_SSL_CONTEXT = False
    mock_settings.SMTP_TLS = False
    mock_settings.SMTP_AUTH = False

    smtp_server = SMTPServer()
    succeed = smtp_server.send_email(EMAILS_TO, 'foo', 'bla bla bla')
    assert succeed is True


@mock.patch('passbot.smtp.smtplib.SMTP_SSL')
@mock.patch('passbot.smtp.settings')
def test_ssl_auth(mock_settings, mock_smtp):
    mock_settings.SMTP_SSL = True
    mock_settings.SMTP_SSL_CONTEXT = True
    mock_settings.SMTP_AUTH = True

    smtp_server = SMTPServer()
    succeed = smtp_server.send_email(EMAILS_TO, 'foo', 'bla bla bla')
    assert succeed is True


@mock.patch('passbot.smtp.smtplib.SMTP_SSL')
@mock.patch('passbot.smtp.settings')
def test_ssl_no_auth(mock_settings, mock_smtp):
    mock_settings.SMTP_SSL = True
    mock_settings.SMTP_SSL_CONTEXT = True
    mock_settings.SMTP_AUTH = False

    smtp_server = SMTPServer()
    succeed = smtp_server.send_email(EMAILS_TO, 'foo', 'bla bla bla')
    assert succeed is True


@mock.patch('passbot.smtp.smtplib.SMTP_SSL')
@mock.patch('passbot.smtp.settings')
def test_exception(mock_settings, mock_smtp, caplog):
    mock_settings.SMTP_SSL = True
    mock_settings.SMTP_SSL_CONTEXT = False
    mock_settings.SMTP_AUTH = True

    mock_smtp.return_value.__enter__.return_value.send_message.side_effect = smtplib.SMTPException('Badaboom')

    smtp_server = SMTPServer()
    with caplog.at_level(level=logging.ERROR, logger='passbot.smtp'):
        succeed = smtp_server.send_email(EMAILS_TO, 'foo', 'bla bla bla')

    assert succeed is False
    assert 'Badaboom' in caplog.text
