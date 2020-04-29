from django.contrib.auth.models import User
from django.test import TestCase

from users.models import UserConfig


class UserConfigTest(TestCase):

    def setUp(self):

        user = User.objects.create_user(username='testuser')
        user.config.data = {
            'a': True,
            'b': {
                'foo': 101,
                'bar': 102,
            },
            'c': {
                'foo': {
                    'x': 201,
                },
                'bar': {
                    'y': 202,
                },
                'baz': {
                    'z': 203,
                }
            }
        }
        user.config.save()

        self.userconfig = user.config

    def test_get(self):
        userconfig = self.userconfig

        # Retrieve root and nested values
        self.assertEqual(userconfig.get('a'), True)
        self.assertEqual(userconfig.get('b.foo'), 101)
        self.assertEqual(userconfig.get('c.baz.z'), 203)

        # Invalid values should return None
        self.assertIsNone(userconfig.get('invalid'))
        self.assertIsNone(userconfig.get('a.invalid'))
        self.assertIsNone(userconfig.get('b.foo.invalid'))
        self.assertIsNone(userconfig.get('b.foo.x.invalid'))

        # Invalid values with a provided default should return the default
        self.assertEqual(userconfig.get('invalid', 'DEFAULT'), 'DEFAULT')
        self.assertEqual(userconfig.get('a.invalid', 'DEFAULT'), 'DEFAULT')
        self.assertEqual(userconfig.get('b.foo.invalid', 'DEFAULT'), 'DEFAULT')
        self.assertEqual(userconfig.get('b.foo.x.invalid', 'DEFAULT'), 'DEFAULT')

    def test_all(self):
        userconfig = self.userconfig
        flattened_data = {
            'a': True,
            'b.foo': 101,
            'b.bar': 102,
            'c.foo.x': 201,
            'c.bar.y': 202,
            'c.baz.z': 203,
        }

        # Retrieve a flattened dictionary containing all config data
        self.assertEqual(userconfig.all(), flattened_data)

    def test_set(self):
        userconfig = self.userconfig

        # Overwrite existing values
        userconfig.set('a', 'abc')
        userconfig.set('c.foo.x', 'abc')
        self.assertEqual(userconfig.data['a'], 'abc')
        self.assertEqual(userconfig.data['c']['foo']['x'], 'abc')

        # Create new values
        userconfig.set('d', 'abc')
        userconfig.set('b.baz', 'abc')
        self.assertEqual(userconfig.data['d'], 'abc')
        self.assertEqual(userconfig.data['b']['baz'], 'abc')

        # Set a value and commit to the database
        userconfig.set('a', 'def', commit=True)

        userconfig.refresh_from_db()
        self.assertEqual(userconfig.data['a'], 'def')

        # Attempt to change a branch node to a leaf node
        with self.assertRaises(TypeError):
            userconfig.set('b', 1)

        # Attempt to change a leaf node to a branch node
        with self.assertRaises(TypeError):
            userconfig.set('a.x', 1)

    def test_clear(self):
        userconfig = self.userconfig

        # Clear existing values
        userconfig.clear('a')
        userconfig.clear('b.foo')
        self.assertTrue('a' not in userconfig.data)
        self.assertTrue('foo' not in userconfig.data['b'])
        self.assertEqual(userconfig.data['b']['bar'], 102)

        # Clear a non-existing value; should fail silently
        userconfig.clear('invalid')
