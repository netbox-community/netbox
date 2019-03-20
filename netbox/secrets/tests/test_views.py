import urllib.parse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole


class SecretRoleTestCase(TestCase):

    def setUp(self):

        TEST_USERNAME = 'testuser'
        TEST_PASSWORD = 'testpassword'

        User = get_user_model()
        User.objects.create(username=TEST_USERNAME, email='testuser@example.com', password=TEST_PASSWORD)

        self.client = Client()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        SecretRole.objects.bulk_create([
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
            SecretRole(name='Secret Role 3', slug='secret-role-3'),
        ])

    def test_secretrole_list(self):

        url = reverse('secrets:secret_list')

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


class SecretTestCase(TestCase):

    def setUp(self):

        self.client = Client()

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

    def test_configcontext(self):

        secret = Secret.objects.first()
        response = self.client.get(secret.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
