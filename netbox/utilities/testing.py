from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.test import APITestCase as _APITestCase

from users.models import Token


class APITestCase(_APITestCase):

    def setUp(self):
        """
        Create a superuser and token for API calls.
        """
        self.user = User.objects.create(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key)}

    def assertHttpStatus(self, response, expected_status):
        """
        Provide more detail in the event of an unexpected HTTP response.
        """
        err_message = "Expected HTTP status {}; received {}: {}"
        self.assertEqual(response.status_code, expected_status, err_message.format(
            expected_status, response.status_code, response.data
        ))
