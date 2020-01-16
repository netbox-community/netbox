import base64
import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.testing import create_test_user
from .constants import PRIVATE_KEY, PUBLIC_KEY


class SecretRoleTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'secrets.view_secretrole',
                'secrets.add_secretrole',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        SecretRole.objects.bulk_create([
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
            SecretRole(name='Secret Role 3', slug='secret-role-3'),
        ])

    def test_secretrole_list(self):

        url = reverse('secrets:secretrole_list')

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_secretrole_import(self):

        csv_data = (
            "name,slug",
            "Secret Role 4,secret-role-4",
            "Secret Role 5,secret-role-5",
            "Secret Role 6,secret-role-6",
        )

        response = self.client.post(reverse('secrets:secretrole_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SecretRole.objects.count(), 6)


class SecretTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'secrets.view_secret',
                'secrets.add_secret',
            ]
        )

        # Set up a master key
        userkey = UserKey(user=user, public_key=PUBLIC_KEY)
        userkey.save()
        master_key = userkey.get_master_key(PRIVATE_KEY)
        self.session_key = SessionKey(userkey=userkey)
        self.session_key.save(master_key)

        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(manufacturer=manufacturer, model='Device Type 1')
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device.save()

        secretrole = SecretRole(name='Secret Role 1', slug='secret-role-1')
        secretrole.save()

        Secret.objects.bulk_create([
            Secret(device=device, role=secretrole, name='Secret 1', ciphertext=b'1234567890'),
            Secret(device=device, role=secretrole, name='Secret 2', ciphertext=b'1234567890'),
            Secret(device=device, role=secretrole, name='Secret 3', ciphertext=b'1234567890'),
        ])

    def test_secret_list(self):

        url = reverse('secrets:secret_list')
        params = {
            "role": SecretRole.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_secret(self):

        secret = Secret.objects.first()
        response = self.client.get(secret.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_secret_import(self):

        csv_data = (
            "device,role,name,plaintext",
            "Device 1,Secret Role 1,Secret 4,abcdefghij",
            "Device 1,Secret Role 1,Secret 5,abcdefghij",
            "Device 1,Secret Role 1,Secret 6,abcdefghij",
        )

        # Set the session_key cookie on the request
        session_key = base64.b64encode(self.session_key.key).decode('utf-8')
        self.client.cookies['session_key'] = session_key

        response = self.client.post(reverse('secrets:secret_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Secret.objects.count(), 6)
