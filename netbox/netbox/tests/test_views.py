import urllib.parse

from utilities.testing import TestCase
from django.urls import reverse


class HomeViewTestCase(TestCase):

    def test_home(self):

        url = reverse('home')

        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_search(self):

        url = reverse('search')
        params = {
            'q': 'foo',
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)
