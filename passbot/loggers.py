import logging.config
from typing import Any

from passbot import settings

handlers: dict[str, Any] = {
    'console': {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'default',
    },
}
if settings.PASSBOT_LOG_FILE_PATH:
    handlers['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'DEBUG',
        'formatter': 'default',
        'filename': settings.PASSBOT_LOG_FILE_PATH,
        'maxBytes': settings.PASSBOT_LOG_FILE_MAX_BYTES,
        'backupCount': settings.PASSBOT_LOG_FILE_BACKUP_COUNT,
    }

conf: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': handlers,
    'root': {
        'handlers': settings.PASSBOT_LOG_HANDLERS,
        'level': settings.PASSBOT_LOG_LEVEL,
    },
}


def load_loggers() -> None:
    logging.config.dictConfig(conf)
