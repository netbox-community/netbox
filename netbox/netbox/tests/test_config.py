from django.conf import settings
from django.core.cache import cache
from django.test import override_settings, TestCase

from extras.models import ConfigRevision
from netbox.config import clear_config, get_config


# Prefix cache keys to avoid interfering with the local environment
CACHES = settings.CACHES
CACHES['default'].update({'KEY_PREFIX': 'TEST-'})


class ConfigTestCase(TestCase):

    @override_settings(CACHES=CACHES)
    def test_config_init_empty(self):
        cache.clear()

        config = get_config()
        self.assertEqual(config.config, {})
        self.assertEqual(config.version, None)

        clear_config()

    @override_settings(CACHES=CACHES)
    def test_config_init_from_db(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        cache.clear()

        # Create a config but don't load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

        clear_config()

    @override_settings(CACHES=CACHES)
    def test_config_init_from_cache(self):
        CONFIG_DATA = {'BANNER_TOP': 'B'}
        cache.clear()

        # Create a config and load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        configrevision.activate()

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

        clear_config()
