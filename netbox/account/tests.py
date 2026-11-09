from django.test import override_settings
from django.urls import reverse

from users.models import Token
from utilities.testing import TestCase


@override_settings(DEFAULT_PERMISSIONS={
    'users.change_token': ({'user': '$user'},),
})
class UserTokenEditTestCase(TestCase):

    def test_edit_own_token(self):
        token = Token.objects.create(user=self.user, description='Original description')
        url = reverse('account:usertoken_edit', kwargs={'pk': token.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'description': 'Updated description',
            'enabled': 'on',
        })
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertEqual(token.description, 'Updated description')
        self.assertEqual(token.user, self.user)
