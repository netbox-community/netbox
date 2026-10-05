from django.conf import settings
from django.test import override_settings, tag
from django.test.client import RequestFactory
from django.urls import reverse

from dcim.models import Site
from dcim.tables import SiteTable
from netbox.config import get_config
from users.models import User, UserConfig
from users.preferences import UserPreference
from utilities.testing import TestCase

DEFAULT_USER_PREFERENCES = {
    'pagination': {
        'per_page': 250,
    }
}


class UserPreferencesTestCase(TestCase):
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

    @tag('regression')  # Ref: #23283
    @override_settings(DEFAULT_USER_PREFERENCES={'locale': {'language': 'de'}, 'pagination': {'per_page': 25}})
    def test_login_creates_missing_userconfig(self):
        """A login without a UserConfig creates one from a copy of the default preferences."""
        user = User.objects.create_user(username='User 1', password='pw')
        UserConfig.objects.filter(user=user).delete()

        self.client.logout()
        response = self.client.post(reverse('login'), {'username': 'User 1', 'password': 'pw'})

        defaults = {'locale': {'language': 'de'}, 'pagination': {'per_page': 25}}
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserConfig.objects.get(user=user).data, defaults)
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'de')

        userconfig = response.wsgi_request.user.config
        userconfig.set('pagination.per_page', 50)
        userconfig.clear('locale.language')
        self.assertEqual(get_config().DEFAULT_USER_PREFERENCES, defaults)

    def test_table_ordering(self):
        url = reverse('dcim:site_list')
        response = self.client.get(f"{url}?sort=status")
        self.assertEqual(response.status_code, 200)

        # Check that table ordering preference has been recorded
        self.user.refresh_from_db()
        ordering = self.user.config.get('tables.SiteTable.ordering')
        self.assertEqual(ordering, ['status'])

        # Check that a recorded preference is honored by default
        self.user.config.set('tables.SiteTable.ordering', ['-status'], commit=True)
        table = SiteTable(Site.objects.all())
        request = RequestFactory().get(url)
        request.user = self.user
        table.configure(request)
        self.assertEqual(table.order_by, ('-status',))
