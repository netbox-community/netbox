import urllib.parse

from django.test import TestCase
from django.urls import reverse


class HomeViewTestCase(TestCase):

    def test_home(self):

        url = reverse('home')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search(self):

        url = reverse('search')
        params = {
            'q': 'foo',
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)
