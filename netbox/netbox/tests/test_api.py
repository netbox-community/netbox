import uuid

from django.urls import reverse

from utilities.testing import APITestCase


class AppTest(APITestCase):

    def test_http_headers(self):
        response = self.client.get(reverse('api-root'), **self.header)

        # Check that all custom response headers are present and valid
        self.assertEqual(response.status_code, 200)
        request_id = response.headers['X-Request-ID']
        uuid.UUID(request_id)

    def test_root(self):
        url = reverse('api-root')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)

    def test_status(self):
        url = reverse('api-status')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)
