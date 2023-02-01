import logging.config
import os

from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('PASSBOT_LOG_PATH', '/tmp/passbot.log'),
            'maxBytes': 1024,
            'backupCount': 3,
        },
    },
    'loggers': {
        'passbot': {
            'handlers': ['console', 'file'],
            'level': os.getenv('PASSBOT_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
})
