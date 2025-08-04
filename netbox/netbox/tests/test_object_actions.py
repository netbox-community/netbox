from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from dcim.models import Device
from netbox.object_actions import AddObject, BulkImport
from netbox.tests.dummy_plugin.models import DummyNetBoxModel


class ObjectActionTest(TestCase):

    def test_get_url_core_model(self):
        """Test URL generation for core NetBox models"""
        obj = Device()

        url = AddObject.get_url(obj)
        self.assertEqual(url, '/dcim/devices/add/')

        url = BulkImport.get_url(obj)
        self.assertEqual(url, '/dcim/devices/import/')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    def test_get_url_plugin_model(self):
        """Test URL generation for plugin models includes plugins: namespace"""
        obj = DummyNetBoxModel()

        url = AddObject.get_url(obj)
        self.assertEqual(url, '/plugins/dummy-plugin/netboxmodel/add/')

        url = BulkImport.get_url(obj)
        self.assertEqual(url, '/plugins/dummy-plugin/netboxmodel/import/')
