from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from extras.registry import registry
from extras.tests.dummy_plugin.models import DummyModel
from extras.tests.dummy_plugin.template_content import SiteContent


class PluginTest(TestCase):

    def test_config(self):

        self.assertIn('extras.tests.dummy_plugin.DummyPluginConfig', settings.INSTALLED_APPS)

    def test_models(self):

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
        self.assertIn(SiteContent, registry['plugin_template_extensions']['dcim.site'])

    def test_middleware(self):
        """
        Check that plugin middleware is registered.
        """
        self.assertIn('extras.tests.dummy_plugin.middleware.DummyMiddleware', settings.MIDDLEWARE)
