from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from core.models import ObjectChange
from dcim.models import Site
from netbox.tests.dummy_plugin.models import DummyNetBoxModel


class ModelTestCase(TestCase):

    def test_get_absolute_url(self):
        m = ObjectChange()
        m.pk = 123

        self.assertEqual(m.get_absolute_url(), f'/core/changelog/{m.pk}/')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    def test_get_absolute_url_plugin(self):
        m = DummyNetBoxModel()
        m.pk = 123

        self.assertEqual(m.get_absolute_url(), f'/plugins/dummy-plugin/netboxmodel/{m.pk}/')


class DeleteMixinTestCase(TestCase):

    def test_delete_unsaved_instance_raises_value_error(self):
        """Deleting an instance with no primary key raises ValueError."""
        site = Site(name='Site 1', slug='site-1')
        with self.assertRaises(ValueError):
            site.delete()
