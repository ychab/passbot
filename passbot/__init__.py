from passbot.config import Settings

settings: Settings = Settings()

from passbot.loggers import load_loggers  # noqa

load_loggers()
