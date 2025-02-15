from django.test import TestCase

from core.models import ObjectChange
from netbox.tests.dummy_plugin.models import DummyModel


class ModelTest(TestCase):

    def test_get_absolute_url(self):
        m = ObjectChange()
        m.pk = 123

        self.assertEqual(m.get_absolute_url(), f'/core/changelog/{m.pk}/')

    def test_absolute_url(self):
        m = DummyModel(name='Foo')
        m.full_clean()
        m.save()

        self.assertEqual(m.get_absolute_url(), f"/plugins/dummy-plugin/models/{m.pk}/")
