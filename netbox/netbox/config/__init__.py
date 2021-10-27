import logging
import threading

from django.conf import settings
from django.core.cache import cache
from django.db.utils import DatabaseError

from .parameters import PARAMS

__all__ = (
    'clear_config',
    'ConfigItem',
    'get_config',
    'PARAMS',
)

_thread_locals = threading.local()

logger = logging.getLogger('netbox.config')


def get_config():
    """
    Return the current NetBox configuration, pulling it from cache if not already loaded in memory.
    """
    if not hasattr(_thread_locals, 'config'):
        _thread_locals.config = Config()
        logger.debug("Initialized configuration")
    return _thread_locals.config


def clear_config():
    """
    Delete the currently loaded configuration, if any.
    """
    if hasattr(_thread_locals, 'config'):
        del _thread_locals.config
        logger.debug("Cleared configuration")


class Config:
    """
    Fetch and store in memory the current NetBox configuration. This class must be instantiated prior to access, and
    must be re-instantiated each time it's necessary to check for updates to the cached config.
    """
    def __init__(self):
        self._populate_from_cache()
        if not self.config or not self.version:
            self._populate_from_db()
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

    def _populate_from_cache(self):
        """Populate config data from Redis cache"""
        self.config = cache.get('config') or {}
        self.version = cache.get('config_version')
        if self.config:
            logger.debug("Loaded configuration data from cache")

    def _populate_from_db(self):
        """Cache data from latest ConfigRevision, then populate from cache"""
        from extras.models import ConfigRevision

        try:
            revision = ConfigRevision.objects.last()
            logger.debug("Loaded configuration data from database")
        except DatabaseError:
            # The database may not be available yet (e.g. when running a management command)
            logger.warning(f"Skipping config initialization (database unavailable)")
            return

        if revision is None:
            logger.debug("No previous configuration found in database; proceeding with default values")
            return

        revision.activate()
        logger.debug("Filled cache with data from latest ConfigRevision")
        self._populate_from_cache()


class ConfigItem:
    """
    A callable to retrieve a configuration parameter from the cache. This can serve as a placeholder to defer
    referencing a configuration parameter.
    """
    def __init__(self, item):
        self.item = item

    def __call__(self):
        config = get_config()
        return getattr(config, self.item)
