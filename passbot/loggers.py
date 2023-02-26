import logging.config

from passbot import settings

conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': settings.PASSBOT_LOG_PATH,
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': settings.PASSBOT_LOG_HANDLERS,
        'level': settings.PASSBOT_LOG_LEVEL,
    },
}


def load_loggers() -> None:
    logging.config.dictConfig(conf)
