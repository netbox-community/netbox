import logging
import threading

from django.conf import settings
from django.core.cache import cache
from django.db.utils import DatabaseError
from django.utils.translation import gettext_lazy as _

from .parameters import PARAMS

__all__ = (
    'PARAMS',
    'Config',
    'ConfigItem',
    'clear_config',
    'get_config',
)

_thread_locals = threading.local()

logger = logging.getLogger('netbox.config')

# Sentinel used to distinguish a cache miss from a cached "empty" config (an empty dict is a
# legitimate cached value when no ConfigRevision exists).
_MISSING = object()


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
        # Only consult the database when the cache has genuinely never been populated. A cached
        # empty config (no ConfigRevision) is authoritative and must not trigger a re-query.
        if self._cache_miss:
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

        raise AttributeError(_("Invalid configuration parameter: {item}").format(item=item))

    def _populate_from_cache(self):
        """Populate config data from Redis cache"""
        cached_config = cache.get('config', _MISSING)
        cached_version = cache.get('config_version', _MISSING)

        # Treat the cache as warm only when both keys are present. A missing 'config_version'
        # (e.g. evicted or never written) must re-query the database, even if 'config' is cached.
        # The no-revision branch writes both keys (config={}, config_version=None), so the
        # intentional empty state is still a cache hit.
        self._cache_miss = cached_config is _MISSING or cached_version is _MISSING

        # A cached value of None (ConfigRevision.data is nullable) or {} is a legitimate empty
        # config and must not crash attribute access; normalize it to an empty dict.
        self.config = {} if cached_config is _MISSING else (cached_config or {})
        self.version = None if cached_version is _MISSING else cached_version
        if self.config:
            logger.debug("Loaded configuration data from cache")

    def _populate_from_db(self):
        """Cache data from latest ConfigRevision, then populate from cache"""
        from core.models import ConfigRevision

        try:
            # Enforce the creation date as the ordering parameter
            revision = ConfigRevision.objects.get(active=True)
            logger.debug(f"Loaded active configuration revision (#{revision.pk})")
        except (ConfigRevision.DoesNotExist, ConfigRevision.MultipleObjectsReturned):
            revision = ConfigRevision.objects.order_by('-created').first()
            if revision is None:
                logger.debug("No configuration found in database; proceeding with default values")
                # Cache the empty state so subsequent requests are served from the cache rather than
                # re-querying the database on every request (#22158). Creating the first
                # ConfigRevision overwrites this via the post_save handler.
                cache.set('config', {}, None)
                cache.set('config_version', None, None)
                self._populate_from_cache()
                return
            logger.debug(f"No active configuration revision found; falling back to most recent (#{revision.pk})")
        except DatabaseError:
            # The database may not be available yet (e.g. when running a management command). Do NOT
            # cache anything here, so the next instantiation re-queries once the database is reachable.
            logger.warning("Skipping config initialization (database unavailable)")
            return

        revision.activate(update_db=False)
        self._populate_from_cache()
        logger.debug("Filled cache with data from latest ConfigRevision")


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
