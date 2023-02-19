from django.test import TestCase

from netbox.registry import Registry


class RegistryTest(TestCase):

    def test_set_store(self):
        reg = Registry({
            'foo': 123,
        })
        with self.assertRaises(TypeError):
            reg['bar'] = 456

    def test_mutate_store(self):
        reg = Registry({
            'foo': [1, 2],
        })
        reg['foo'].append(3)
        self.assertListEqual(reg['foo'], [1, 2, 3])

    def test_delete_store(self):
        reg = Registry({
            'foo': 123,
        })
        with self.assertRaises(TypeError):
            del reg['foo']
