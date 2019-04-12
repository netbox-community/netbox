from django.contrib.auth.models import Permission, User
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


def create_test_user(username='testuser', permissions=list()):
    """
    Create a User with the given permissions.
    """
    user = User.objects.create_user(username=username)
    for perm_name in permissions:
        app, codename = perm_name.split('.')
        perm = Permission.objects.get(content_type__app_label=app, codename=codename)
        user.user_permissions.add(perm)

    return user
