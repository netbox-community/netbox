from unittest import skipIf

from django.conf import settings
from django.test import RequestFactory, TestCase

from dcim.models import Device, DeviceType, Manufacturer
from netbox.object_actions import AddObject, BulkEdit, BulkImport


class ObjectActionTest(TestCase):

    def test_get_url_core_model(self):
        """Test URL generation for core NetBox models"""
        obj = Device()

        url = AddObject.get_url(obj)
        self.assertEqual(url, '/dcim/devices/add/')

        url = BulkImport.get_url(obj)
        self.assertEqual(url, '/dcim/devices/import/')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_get_url_plugin_model(self):
        """Test URL generation for plugin models includes plugins: namespace"""
        from netbox.tests.dummy_plugin.models import DummyNetBoxModel

        obj = DummyNetBoxModel()

        url = AddObject.get_url(obj)
        self.assertEqual(url, '/plugins/dummy-plugin/netboxmodel/add/')

        url = BulkImport.get_url(obj)
        self.assertEqual(url, '/plugins/dummy-plugin/netboxmodel/import/')

    def test_bulk_edit_get_context_child_object(self):
        """
        Test that the parent object's PK is included in the context for child objects.

        Ensure that BulkEdit.get_context() correctly identifies and
        includes the parent object's PK when rendering a child object's
        action button.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')

        # Mock context containing the parent object (DeviceType)
        request = RequestFactory().get('/')
        context = {
            'request': request,
            'object': device_type,
        }

        # Get context for the child model (Device)
        action_context = BulkEdit.get_context(context, Device)

        # Verify that 'device_type' (the FK field name) is present in
        # url_params with the parent's PK
        self.assertIn('url_params', action_context)
        self.assertEqual(action_context['url_params'].get('device_type'), device_type.pk)
