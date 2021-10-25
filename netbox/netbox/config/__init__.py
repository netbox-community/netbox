from django.conf import settings
from django.core.cache import cache

from .parameters import PARAMS

__all__ = (
    'ConfigResolver',
    'PARAMS',
)


class ConfigResolver:
    """
    Active NetBox configuration.
    """
    def __init__(self):
        self.config = cache.get('config')
        self.version = self.config.get('config_version')
        self.defaults = {param.name: param.default for param in PARAMS}

    def __getattr__(self, item):

        # Check for hard-coded configuration in settings.py
        if hasattr(settings, item):
            return getattr(settings, item)

        # Return config value from cache
        if item in self.config:
            return self.config[item]

        # Fall back to the parameter's default value
        if item in self.defaults:
            return self.defaults[item]

        raise AttributeError(f"Invalid configuration parameter: {item}")
