import logging.config

from passbot.config import settings

conf = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-8s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': settings.PASSBOT_LOG_PATH,
            'formatter': 'default',
            'maxBytes': 1024,
            'backupCount': 3,
        },
    },
    'loggers': {
        'passbot': {
            'handlers': ['console', 'file'],
            'level': settings.PASSBOT_LOG_LEVEL,
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


def load_loggers() -> None:
    logging.config.dictConfig(conf)
