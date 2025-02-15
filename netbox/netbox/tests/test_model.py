from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from core.models import ObjectChange
from netbox.tests.dummy_plugin.models import DummyNetBoxModel


class ModelTest(TestCase):

    def test_get_absolute_url(self):
        m = ObjectChange()
        m.pk = 123

        self.assertEqual(m.get_absolute_url(), f'/core/changelog/{m.pk}/')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    def test_get_absolute_url_plugin(self):
        m = DummyNetBoxModel()
        m.pk = 123

        self.assertEqual(m.get_absolute_url(), f'/plugins/dummy-plugin/netboxmodel/{m.pk}/')
