from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from users.choices import TokenVersionChoices
from users.models import Token, User
from utilities.testing import create_test_user


class TokenTest(TestCase):
    """
    Test class for testing the functionality of the Token model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the Token model.
        """
        cls.user = create_test_user('User 1')

    def test_is_active(self):
        """
        Test the is_active property.
        """
        # Token with enabled status and no expiration date
        token = Token(user=self.user, enabled=True, expires=None)
        self.assertTrue(token.is_active)

        # Token with disabled status
        token.enabled = False
        self.assertFalse(token.is_active)

        # Token with enabled status and future expiration
        future_date = timezone.now() + timedelta(days=1)
        token = Token(user=self.user, enabled=True, expires=future_date)
        self.assertTrue(token.is_active)

        # Token with past expiration
        token.expires = timezone.now() - timedelta(days=1)
        self.assertFalse(token.is_active)

        # Token with disabled status and past expiration
        past_date = timezone.now() - timedelta(days=1)
        token = Token(user=self.user, enabled=False, expires=past_date)
        self.assertFalse(token.is_active)

    def test_is_expired(self):
        """
        Test the is_expired property.
        """
        # Token with no expiration
        token = Token(user=self.user, expires=None)
        self.assertFalse(token.is_expired)

        # Token with future expiration
        token.expires = timezone.now() + timedelta(days=1)
        self.assertFalse(token.is_expired)

        # Token with past expiration
        token.expires = timezone.now() - timedelta(days=1)
        self.assertTrue(token.is_expired)

    def test_cannot_create_token_with_past_expiration(self):
        """
        Test that creating a token with an expiration date in the past raises a ValidationError.
        """
        past_date = timezone.now() - timedelta(days=1)
        token = Token(user=self.user, expires=past_date)

        with self.assertRaises(ValidationError) as cm:
            token.clean()
        self.assertIn('expires', cm.exception.error_dict)

    def test_can_update_existing_expired_token(self):
        """
        Test that updating an already expired token does NOT raise a ValidationError.
        """
        # Create a valid token first with an expiration date in the past
        # bypasses the clean() method
        token = Token.objects.create(user=self.user)
        token.expires = timezone.now() - timedelta(days=1)
        token.save()

        # Try to update the description
        token.description = 'New Description'
        try:
            token.clean()
            token.save()
        except ValidationError:
            self.fail('Updating an expired token should not raise ValidationError')

        token.refresh_from_db()
        self.assertEqual(token.description, 'New Description')

    @override_settings(API_TOKEN_PEPPERS={})
    def test_v2_without_peppers_configured(self):
        """
        Attempting to save a v2 token without API_TOKEN_PEPPERS defined should raise a ValidationError.
        """
        token = Token(version=TokenVersionChoices.V2)
        with self.assertRaises(ValidationError):
            token.clean()


class UserConfigTest(TestCase):

    @classmethod
    def setUpTestData(cls):

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

    def test_get(self):
        userconfig = User.objects.get(username='testuser').config

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
        userconfig = User.objects.get(username='testuser').config
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
        userconfig = User.objects.get(username='testuser').config

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
        userconfig = User.objects.get(username='testuser').config

        # Clear existing values
        userconfig.clear('a')
        userconfig.clear('b.foo')
        self.assertTrue('a' not in userconfig.data)
        self.assertTrue('foo' not in userconfig.data['b'])
        self.assertEqual(userconfig.data['b']['bar'], 102)

        # Clear a non-existing value; should fail silently
        userconfig.clear('invalid')
