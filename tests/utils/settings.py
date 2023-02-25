from typing import Any

from passbot.config import settings


class override_settings:

    def __init__(self, **kwargs):
        self.ori_settings = settings.copy(deep=True)
        self.options: dict[str, Any] = kwargs

    def __enter__(self):
        for key, val in self.options.items():
            setattr(settings, key, val)

    def __exit__(self, exc_type, exc_value, traceback):
        for key, val in self.options.items():
            setattr(settings, key, getattr(self.ori_settings, key))
