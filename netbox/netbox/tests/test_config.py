from django.core.cache import cache
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from core.models import ConfigRevision
from netbox.config import clear_config, get_config


def _configrevision_query_count(queries):
    """Count captured queries that touch the core_configrevision table."""
    return len([q for q in queries if 'core_configrevision' in q['sql']])


# Use a per-process in-memory cache so the shared 'config'/'config_version' keys can't be
# contaminated by other tests running in parallel against the same Redis instance.
@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'netbox-config-tests',
    },
})
class ConfigTestCase(TestCase):

    def setUp(self):
        super().setUp()
        # Register cleanup so it runs after each test, even on assertion failure.
        # clear_config drops the thread-local Config; cache.clear wipes the cache
        # entries that configrevision.activate writes.
        self.addCleanup(cache.clear)
        self.addCleanup(clear_config)

        # Defensive reset against pre-existing state from outside this class.
        clear_config()
        cache.clear()

    def test_config_init_empty(self):
        config = get_config()
        self.assertEqual(config.config, {})
        self.assertEqual(config.version, None)

    def test_empty_config_not_requeried(self):
        # With no ConfigRevision present, the empty state should be cached after the first load so
        # that subsequent requests are served from the cache rather than re-querying the database
        # on every request (#22158).
        with CaptureQueriesContext(connection) as ctx:
            first = get_config()
        self.assertGreaterEqual(_configrevision_query_count(ctx.captured_queries), 1)
        self.assertEqual(first.config, {})
        self.assertEqual(first.version, None)

        # Simulate the request boundary, where the middleware drops the thread-local config.
        clear_config()

        with CaptureQueriesContext(connection) as ctx:
            second = get_config()
        self.assertEqual(_configrevision_query_count(ctx.captured_queries), 0)
        self.assertEqual(second.config, {})
        self.assertEqual(second.version, None)

    def test_empty_then_create_first_revision(self):
        # Prime the cache with the empty state.
        get_config()

        # Creating the first ConfigRevision fires the post_save handler, which activates it and
        # overwrites the cached empty state.
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)

        clear_config()
        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

    def test_config_init_from_cache_null_data(self):
        # ConfigRevision.data is nullable; a revision with data=None caches None. Config access
        # must normalize that to an empty dict rather than crash on attribute lookup.
        configrevision = ConfigRevision.objects.create(data=None)
        configrevision.activate()

        clear_config()
        config = get_config()
        self.assertEqual(config.config, {})
        self.assertEqual(config.version, configrevision.pk)
        # Attribute access must fall back to defaults without raising.
        self.assertEqual(config.BANNER_TOP, '')

    def test_missing_version_key_requeries(self):
        # If 'config_version' is missing (evicted/never written) while 'config' is cached, the
        # cache must be treated as cold and re-populated from the database rather than leaving
        # version=None when a ConfigRevision exists.
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        configrevision.activate()

        # Drop only the version key, leaving 'config' populated.
        cache.delete('config_version')
        clear_config()

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

    def test_config_init_from_db(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}

        # Create a config but don't load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

    def test_config_init_from_cache(self):
        CONFIG_DATA = {'BANNER_TOP': 'B'}

        # Create a config and load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        configrevision.activate()

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

    @override_settings(BANNER_TOP='Z')
    def test_settings_override(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}

        # Create a config and load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        configrevision.activate()

        config = get_config()
        self.assertEqual(config.BANNER_TOP, 'Z')
        self.assertEqual(config.version, configrevision.pk)
