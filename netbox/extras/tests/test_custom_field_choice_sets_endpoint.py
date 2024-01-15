from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.models import Token

User = get_user_model()


class CustomFieldChoiceSetsEndpointTest(APITestCase):

    def setUp(self):
        self.super_user = User.objects.create_user(username='testuser', is_staff=True, is_superuser=True)
        self.token = Token.objects.create(user=self.super_user)
        self.header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        self.url = '/api/extras/custom-field-choice-sets/'

    def test_extra_choices_only_one_choice_element_return_400(self):
        payload = {
            "name": "test",
            "extra_choices": [["choice1"]]
        }

        response = self.client.post(self.url, payload, format='json', **self.header)

        self.assertEqual(response.status_code, 400)

    def test_extra_choices_two_wrong_choice_elements_return_400(self):
        payload = {
            "name": "test",
            "extra_choices": [["choice1"], ["choice2"]]
        }

        response = self.client.post(self.url, payload, format='json', **self.header)

        self.assertEqual(response.status_code, 400)

    def test_extra_choices_one_is_wrong_other_correct_choice_elements_return_400(self):
        payload = {
            "name": "test",
            "extra_choices": [["1A", "choice1"], ["choice2"]]
        }

        response = self.client.post(self.url, payload, format='json', **self.header)

        self.assertEqual(response.status_code, 400)

    def test_extra_choices_correct_choices_return_201(self):
        payload = {
            'name': 'Choice Set',
            'extra_choices': [
                ['4A', 'Choice 1'],
                ['4B', 'Choice 2'],
                ['4C', 'Choice 3'],
            ],
        }

        response = self.client.post(self.url, payload, format='json', **self.header)

        self.assertEqual(response.status_code, 201)
