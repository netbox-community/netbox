from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings

from core.models import ConfigRevision
from netbox.config import clear_config, get_config

# Prefix cache keys to avoid interfering with the local environment
CACHES = settings.CACHES
CACHES['default'].update({'KEY_PREFIX': 'TEST-'})


@override_settings(CACHES=CACHES)
class ConfigTestCase(TestCase):

    def setUp(self):
        super().setUp()
        # Register cleanup so it runs after each test, even on assertion failure.
        # clear_config drops the thread-local Config; cache.clear wipes the Redis
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
