from django.urls import reverse

from utilities.testing import APITestCase


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)

    def test_status(self):
        url = reverse('api-status')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)
