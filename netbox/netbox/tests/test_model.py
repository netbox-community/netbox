from django.test import TestCase

from netbox.tests.dummy_plugin.models import DummyModel


class ModelTest(TestCase):

    def test_absolute_url(self):
        m = DummyModel(name='Foo')
        m.full_clean()
        m.save()

        self.assertEqual(m.get_absolute_url(), f"/plugins/dummy-plugin/models/{m.pk}/")
