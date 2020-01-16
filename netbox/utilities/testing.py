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
            expected_status, response.status_code, getattr(response, 'data', 'No data')
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


def choices_to_dict(choices_list):
    """
    Convert a list of field choices to a dictionary suitable for direct comparison with a ChoiceSet. For example:

        [
            {
                "value": "choice-1",
                "label": "First Choice"
            },
            {
                "value": "choice-2",
                "label": "Second Choice"
            }
        ]

    Becomes:

        {
            "choice-1": "First Choice",
            "choice-2": "Second Choice
        }
    """
    return {
        choice['value']: choice['label'] for choice in choices_list
    }
