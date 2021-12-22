from django.contrib.auth.models import User
from django.test import override_settings, TestCase

from users.preferences import UserPreference


DEFAULT_USER_PREFERENCES = {
    'pagination': {
        'per_page': 250,
    }
}


class UserPreferencesTest(TestCase):

    def test_userpreference(self):
        CHOICES = (
            ('foo', 'Foo'),
            ('bar', 'Bar'),
        )
        kwargs = {
            'label': 'Test Preference',
            'choices': CHOICES,
            'default': CHOICES[0][0],
            'description': 'Description',
        }
        userpref = UserPreference(**kwargs)

        self.assertEqual(userpref.label, kwargs['label'])
        self.assertEqual(userpref.choices, kwargs['choices'])
        self.assertEqual(userpref.default, kwargs['default'])
        self.assertEqual(userpref.description, kwargs['description'])

    @override_settings(DEFAULT_USER_PREFERENCES=DEFAULT_USER_PREFERENCES)
    def test_default_preferences(self):
        user = User.objects.create(username='User 1')
        userconfig = user.config

        self.assertEqual(userconfig.data, DEFAULT_USER_PREFERENCES)
