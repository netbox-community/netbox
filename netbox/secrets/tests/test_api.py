import base64

from django.urls import reverse
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from users.models import Token
from utilities.testing import APITestCase, APIViewTestCases, create_test_user
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
            Secret(device=device, role=secret_roles[0], name='Secret 1', plaintext='ABC'),
            Secret(device=device, role=secret_roles[0], name='Secret 2', plaintext='DEF'),
            Secret(device=device, role=secret_roles[0], name='Secret 3', plaintext='GHI'),
        )
        for secret in secrets:
            secret.encrypt(self.master_key)
            secret.save()

        self.create_data = [
            {
                'device': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 4',
                'plaintext': 'JKL',
            },
            {
                'device': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 5',
                'plaintext': 'MNO',
            },
            {
                'device': device.pk,
                'role': secret_roles[1].pk,
                'name': 'Secret 6',
                'plaintext': 'PQR',
            },
        ]

    def prepare_instance(self, instance):
        # Unlock the plaintext prior to evaluation of the instance
        instance.decrypt(self.master_key)
        return instance
