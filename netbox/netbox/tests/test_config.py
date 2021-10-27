from django.core.cache import cache
from django.test import TestCase

from extras.models import ConfigRevision
from netbox.config import clear_config, get_config


class ConfigTestCase(TestCase):

    def test_config_init_empty(self):
        cache.clear()

        config = get_config()
        self.assertEqual(config.config, {})
        self.assertEqual(config.version, None)

        clear_config()

    def test_config_init_from_db(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        cache.clear()

        # Create a config but don't load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

        clear_config()

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
