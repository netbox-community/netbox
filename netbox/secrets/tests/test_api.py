import base64

from django.urls import reverse
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.testing import APITestCase, APIViewTestCases
from .constants import PRIVATE_KEY, PUBLIC_KEY


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('secrets-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class SecretRoleTest(APIViewTestCases.APIViewTestCase):
    model = SecretRole
    brief_fields = ['id', 'name', 'secret_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Secret Role 4',
            'slug': 'secret-role-4',
        },
        {
            'name': 'Secret Role 5',
            'slug': 'secret-role-5',
        },
        {
            'name': 'Secret Role 6',
            'slug': 'secret-role-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        secret_roles = (
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
            SecretRole(name='Secret Role 3', slug='secret-role-3'),
        )
        SecretRole.objects.bulk_create(secret_roles)


class SecretTest(APIViewTestCases.APIViewTestCase):
    model = Secret
    brief_fields = ['id', 'name', 'url']

    def setUp(self):
        super().setUp()

        # Create a UserKey for the test user
        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()

        # Create a SessionKey for the user
        self.master_key = userkey.get_master_key(PRIVATE_KEY)
        session_key = SessionKey(userkey=userkey)
        session_key.save(self.master_key)

        # Append the session key to the test client's request header
        self.header['HTTP_X_SESSION_KEY'] = base64.b64encode(session_key.key)

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        device = Device.objects.create(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)

        secret_roles = (
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
        )
        SecretRole.objects.bulk_create(secret_roles)

        secrets = (
            Secret(assigned_object=device, role=secret_roles[0], name='Secret 1', plaintext='ABC'),
            Secret(assigned_object=device, role=secret_roles[0], name='Secret 2', plaintext='DEF'),
            Secret(assigned_object=device, role=secret_roles[0], name='Secret 3', plaintext='GHI'),
        )
        for secret in secrets:
            secret.encrypt(self.master_key)
            secret.save()

        self.create_data = [
            {
                'assigned_object_type': 'dcim.device',
                'assigned_object_id': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 4',
                'plaintext': 'JKL',
            },
            {
                'assigned_object_type': 'dcim.device',
                'assigned_object_id': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 5',
                'plaintext': 'MNO',
            },
            {
                'assigned_object_type': 'dcim.device',
                'assigned_object_id': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 6',
                'plaintext': 'PQR',
            },
        ]

        self.bulk_update_data = {
            'role': secret_roles[1].pk,
        }

    def prepare_instance(self, instance):
        # Unlock the plaintext prior to evaluation of the instance
        instance.decrypt(self.master_key)
        return instance


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
