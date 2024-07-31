from django.test import override_settings
from django.test.client import RequestFactory
from django.urls import reverse

from dcim.models import Site
from dcim.tables import SiteTable
from users.models import User
from users.preferences import UserPreference
from utilities.testing import TestCase


DEFAULT_USER_PREFERENCES = {
    'pagination': {
        'per_page': 250,
    }
}


class UserPreferencesTest(TestCase):
    user_permissions = ['dcim.view_site']

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

    def test_table_ordering(self):
        url = reverse('dcim:site_list')
        response = self.client.get(f"{url}?sort=status")
        self.assertEqual(response.status_code, 200)

        # Check that table ordering preference has been recorded
        self.user.refresh_from_db()
        ordering = self.user.config.get(f'tables.SiteTable.ordering')
        self.assertEqual(ordering, ['status'])

        # Check that a recorded preference is honored by default
        self.user.config.set(f'tables.SiteTable.ordering', ['-status'], commit=True)
        table = SiteTable(Site.objects.all())
        request = RequestFactory().get(url)
        request.user = self.user
        table.configure(request)
        self.assertEqual(table.order_by, ('-status',))
