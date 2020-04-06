from unittest import skipIf

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from extras.registry import registry
from extras.tests.dummy_plugin import config as dummy_config


@skipIf('extras.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
class PluginTest(TestCase):

    def test_config(self):

        self.assertIn('extras.tests.dummy_plugin.DummyPluginConfig', settings.INSTALLED_APPS)

    def test_models(self):
        from extras.tests.dummy_plugin.models import DummyModel

        # Test saving an instance
        instance = DummyModel(name='Instance 1', number=100)
        instance.save()
        self.assertIsNotNone(instance.pk)

        # Test deleting an instance
        instance.delete()
        self.assertIsNone(instance.pk)

    def test_admin(self):

        # Test admin view URL resolution
        url = reverse('admin:dummy_plugin_dummymodel_add')
        self.assertEqual(url, '/admin/dummy_plugin/dummymodel/add/')

    def test_views(self):

        # Test URL resolution
        url = reverse('plugins:dummy_plugin:dummy_models')
        self.assertEqual(url, '/plugins/dummy-plugin/models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_api_views(self):

        # Test URL resolution
        url = reverse('plugins-api:dummy_plugin-api:dummymodel-list')
        self.assertEqual(url, '/api/plugins/dummy-plugin/dummy-models/')

        # Test GET request
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_menu_items(self):
        """
        Check that plugin MenuItems and MenuButtons are registered.
        """
        self.assertIn('Dummy plugin', registry['plugin_menu_items'])
        menu_items = registry['plugin_menu_items']['Dummy plugin']
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(len(menu_items[0].buttons), 2)

    def test_template_extensions(self):
        """
        Check that plugin TemplateExtensions are registered.
        """
        from extras.tests.dummy_plugin.template_content import SiteContent

        self.assertIn(SiteContent, registry['plugin_template_extensions']['dcim.site'])

    def test_middleware(self):
        """
        Check that plugin middleware is registered.
        """
        self.assertIn('extras.tests.dummy_plugin.middleware.DummyMiddleware', settings.MIDDLEWARE)

    def test_caching_config(self):
        """
        Check that plugin caching configuration is registered.
        """
        self.assertIn('extras.tests.dummy_plugin.*', settings.CACHEOPS)

    @override_settings(VERSION='0.9')
    def test_min_version(self):
        """
        Check enforcement of minimum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({})

    @override_settings(VERSION='10.0')
    def test_max_version(self):
        """
        Check enforcement of maximum NetBox version.
        """
        with self.assertRaises(ImproperlyConfigured):
            dummy_config.validate({})

    def test_required_settings(self):
        """
        Validate enforcement of required settings.
        """
        class DummyConfigWithRequiredSettings(dummy_config):
            required_settings = ['foo']

        # Validation should pass when all required settings are present
        DummyConfigWithRequiredSettings.validate({'foo': True})

        # Validation should fail when a required setting is missing
        with self.assertRaises(ImproperlyConfigured):
            DummyConfigWithRequiredSettings.validate({})

    def test_default_settings(self):
        """
        Validate population of default config settings.
        """
        class DummyConfigWithDefaultSettings(dummy_config):
            default_settings = {
                'bar': 123,
            }

        # Populate the default value if setting has not been specified
        user_config = {}
        DummyConfigWithDefaultSettings.validate(user_config)
        self.assertEqual(user_config['bar'], 123)

        # Don't overwrite specified values
        user_config = {'bar': 456}
        DummyConfigWithDefaultSettings.validate(user_config)
        self.assertEqual(user_config['bar'], 456)
