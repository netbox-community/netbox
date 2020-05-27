import base64

from django.urls import reverse
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from users.models import Token
from utilities.testing import APITestCase, create_test_user
from .constants import PRIVATE_KEY, PUBLIC_KEY


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('secrets-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class SecretRoleTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.secretrole1 = SecretRole.objects.create(name='Test Secret Role 1', slug='test-secret-role-1')
        self.secretrole2 = SecretRole.objects.create(name='Test Secret Role 2', slug='test-secret-role-2')
        self.secretrole3 = SecretRole.objects.create(name='Test Secret Role 3', slug='test-secret-role-3')

    def test_get_secretrole(self):

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.secretrole1.name)

    def test_list_secretroles(self):

        url = reverse('secrets-api:secretrole-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_secretroles_brief(self):

        url = reverse('secrets-api:secretrole-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'secret_count', 'slug', 'url']
        )

    def test_create_secretrole(self):

        data = {
            'name': 'Test Secret Role 4',
            'slug': 'test-secret-role-4',
        }

        url = reverse('secrets-api:secretrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(SecretRole.objects.count(), 4)
        secretrole4 = SecretRole.objects.get(pk=response.data['id'])
        self.assertEqual(secretrole4.name, data['name'])
        self.assertEqual(secretrole4.slug, data['slug'])

    def test_create_secretrole_bulk(self):

        data = [
            {
                'name': 'Test Secret Role 4',
                'slug': 'test-secret-role-4',
            },
            {
                'name': 'Test Secret Role 5',
                'slug': 'test-secret-role-5',
            },
            {
                'name': 'Test Secret Role 6',
                'slug': 'test-secret-role-6',
            },
        ]

        url = reverse('secrets-api:secretrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(SecretRole.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_secretrole(self):

        data = {
            'name': 'Test SecretRole X',
            'slug': 'test-secretrole-x',
        }

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(SecretRole.objects.count(), 3)
        secretrole1 = SecretRole.objects.get(pk=response.data['id'])
        self.assertEqual(secretrole1.name, data['name'])
        self.assertEqual(secretrole1.slug, data['slug'])

    def test_delete_secretrole(self):

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SecretRole.objects.count(), 2)


class SecretTest(APITestCase):
    user_permissions = (
        'secrets.add_secret',
        'secrets.change_secret',
        'secrets.delete_secret',
        'secrets.view_secret',
    )

    def setUp(self):
        super().setUp()

        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()
        self.master_key = userkey.get_master_key(PRIVATE_KEY)
        session_key = SessionKey(userkey=userkey)
        session_key.save(self.master_key)

        self.header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
            'HTTP_X_SESSION_KEY': base64.b64encode(session_key.key),
        }

        self.plaintexts = (
            'Secret #1 Plaintext',
            'Secret #2 Plaintext',
            'Secret #3 Plaintext',
        )

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device Type 1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1')
        self.device = Device.objects.create(
            name='Test Device 1', site=site, device_type=devicetype, device_role=devicerole
        )
        self.secretrole1 = SecretRole.objects.create(name='Test Secret Role 1', slug='test-secret-role-1')
        self.secretrole2 = SecretRole.objects.create(name='Test Secret Role 2', slug='test-secret-role-2')
        self.secret1 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 1', plaintext=self.plaintexts[0]
        )
        self.secret1.encrypt(self.master_key)
        self.secret1.save()
        self.secret2 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 2', plaintext=self.plaintexts[1]
        )
        self.secret2.encrypt(self.master_key)
        self.secret2.save()
        self.secret3 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 3', plaintext=self.plaintexts[2]
        )
        self.secret3.encrypt(self.master_key)
        self.secret3.save()

    def test_get_secret(self):

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})

        # Secret plaintext not be decrypted as the user has not been assigned to the role
        response = self.client.get(url, **self.header)
        self.assertIsNone(response.data['plaintext'])

        # The plaintext should be present once the user has been assigned to the role
        self.secretrole1.users.add(self.user)
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['plaintext'], self.plaintexts[0])

    def test_list_secrets(self):

        url = reverse('secrets-api:secret-list')

        # Secret plaintext not be decrypted as the user has not been assigned to the role
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 3)
        for secret in response.data['results']:
            self.assertIsNone(secret['plaintext'])

        # The plaintext should be present once the user has been assigned to the role
        self.secretrole1.users.add(self.user)
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 3)
        for i, secret in enumerate(response.data['results']):
            self.assertEqual(secret['plaintext'], self.plaintexts[i])

    def test_create_secret(self):

        data = {
            'device': self.device.pk,
            'role': self.secretrole1.pk,
            'name': 'Test Secret 4',
            'plaintext': 'Secret #4 Plaintext',
        }

        url = reverse('secrets-api:secret-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plaintext'], data['plaintext'])
        self.assertEqual(Secret.objects.count(), 4)
        secret4 = Secret.objects.get(pk=response.data['id'])
        secret4.decrypt(self.master_key)
        self.assertEqual(secret4.role_id, data['role'])
        self.assertEqual(secret4.plaintext, data['plaintext'])

    def test_create_secret_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 4',
                'plaintext': 'Secret #4 Plaintext',
            },
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 5',
                'plaintext': 'Secret #5 Plaintext',
            },
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 6',
                'plaintext': 'Secret #6 Plaintext',
            },
        ]

        url = reverse('secrets-api:secret-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Secret.objects.count(), 6)
        self.assertEqual(response.data[0]['plaintext'], data[0]['plaintext'])
        self.assertEqual(response.data[1]['plaintext'], data[1]['plaintext'])
        self.assertEqual(response.data[2]['plaintext'], data[2]['plaintext'])

    def test_update_secret(self):

        data = {
            'device': self.device.pk,
            'role': self.secretrole2.pk,
            'plaintext': 'NewPlaintext',
        }

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['plaintext'], data['plaintext'])
        self.assertEqual(Secret.objects.count(), 3)
        secret1 = Secret.objects.get(pk=response.data['id'])
        secret1.decrypt(self.master_key)
        self.assertEqual(secret1.role_id, data['role'])
        self.assertEqual(secret1.plaintext, data['plaintext'])

    def test_delete_secret(self):

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Secret.objects.count(), 2)


class GetSessionKeyTest(APITestCase):

    def setUp(self):

        super().setUp()

        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()
        master_key = userkey.get_master_key(PRIVATE_KEY)
        self.session_key = SessionKey(userkey=userkey)
        self.session_key.save(master_key)

        self.header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
        }

    def test_get_session_key(self):

        encoded_session_key = base64.b64encode(self.session_key.key).decode()

        url = reverse('secrets-api:get-session-key-list')
        data = {
            'private_key': PRIVATE_KEY,
        }
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('session_key'))
        self.assertNotEqual(response.data.get('session_key'), encoded_session_key)

    def test_get_session_key_preserved(self):

        encoded_session_key = base64.b64encode(self.session_key.key).decode()

        url = reverse('secrets-api:get-session-key-list') + '?preserve_key=True'
        data = {
            'private_key': PRIVATE_KEY,
        }
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data.get('session_key'), encoded_session_key)
