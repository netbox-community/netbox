from django.test import TestCase

from extras.registry import Registry


class RegistryTest(TestCase):

    def test_add_store(self):
        reg = Registry()
        reg['foo'] = 123

        self.assertEqual(reg['foo'], 123)

    def test_manipulate_store(self):
        reg = Registry()
        reg['foo'] = [1, 2]
        reg['foo'].append(3)

        self.assertListEqual(reg['foo'], [1, 2, 3])

    def test_overwrite_store(self):
        reg = Registry()
        reg['foo'] = 123

        with self.assertRaises(KeyError):
            reg['foo'] = 456

    def test_delete_store(self):
        reg = Registry()
        reg['foo'] = 123

        with self.assertRaises(TypeError):
            del(reg['foo'])
