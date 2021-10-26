from django.conf import settings
from django.core.cache import cache

from .parameters import PARAMS

__all__ = (
    'Config',
    'ConfigItem',
    'PARAMS',
)


class Config:
    """
    Fetch and store in memory the current NetBox configuration. This class must be instantiated prior to access, and
    must be re-instantiated each time it's necessary to check for updates to the cached config.
    """
    def __init__(self):
        self.config = cache.get('config')
        self.version = cache.get('config_version')
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


class ConfigItem:
    """
    A callable to retrieve a configuration parameter from the cache. This can serve as a placeholder to defer
    referencing a configuration parameter.
    """
    def __init__(self, item):
        self.item = item

    def __call__(self):
        config = Config()
        return getattr(config, self.item)
