import urllib.parse

from django.urls import reverse
from django.test import Client, override_settings

from dcim.models import Site
from netbox.constants import EMPTY_TABLE_TEXT
from netbox.search.backends import search_backend
from utilities.testing import TestCase


class HomeViewTestCase(TestCase):

    def test_home(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)


class SearchViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site Alpha', slug='alpha', description='Red'),
            Site(name='Site Bravo', slug='bravo', description='Red'),
            Site(name='Site Charlie', slug='charlie', description='Green'),
            Site(name='Site Delta', slug='delta', description='Green'),
            Site(name='Site Echo', slug='echo', description='Blue'),
            Site(name='Site Foxtrot', slug='foxtrot', description='Blue'),
        )
        Site.objects.bulk_create(sites)
        search_backend.cache(sites)

    def test_search(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_search_query(self):
        url = reverse('search')
        params = {
            'q': 'red',
        }
        query = urllib.parse.urlencode(params)

        # Test without view permission
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)

        # Add view permissions & query again. Only matching objects should be listed
        self.add_permissions('dcim.view_site')
        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn('Site Alpha', content)
        self.assertIn('Site Bravo', content)
        self.assertNotIn('Site Charlie', content)
        self.assertNotIn('Site Delta', content)
        self.assertNotIn('Site Echo', content)
        self.assertNotIn('Site Foxtrot', content)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_search_no_results(self):
        url = reverse('search')
        params = {
            'q': 'xxxxxxxxx',  # Matches nothing
        }
        query = urllib.parse.urlencode(params)

        response = self.client.get(f'{url}?{query}')
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(EMPTY_TABLE_TEXT, content)


class MediaViewTestCase(TestCase):

    def test_media_login_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should redirect to login page
        self.assertHttpStatus(response, 302)

    @override_settings(LOGIN_REQUIRED=False)
    def test_media_login_not_required(self):
        url = reverse('media', kwargs={'path': 'foo.txt'})
        response = Client().get(url)

        # Unauthenticated request should return a 404 (not found)
        self.assertHttpStatus(response, 404)
