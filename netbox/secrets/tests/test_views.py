import base64

from django.test import override_settings
from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.testing import ViewTestCases
from .constants import PRIVATE_KEY, PUBLIC_KEY


class SecretRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = SecretRole

    @classmethod
    def setUpTestData(cls):

        SecretRole.objects.bulk_create([
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
            SecretRole(name='Secret Role 3', slug='secret-role-3'),
        ])

        cls.form_data = {
            'name': 'Secret Role X',
            'slug': 'secret-role-x',
            'description': 'A secret role',
        }

        cls.csv_data = (
            "name,slug",
            "Secret Role 4,secret-role-4",
            "Secret Role 5,secret-role-5",
            "Secret Role 6,secret-role-6",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


# TODO: Change base class to PrimaryObjectViewTestCase
class SecretTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = Secret

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 2', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 3', site=site, device_type=devicetype, device_role=devicerole),
        )
        Device.objects.bulk_create(devices)

        secretroles = (
            SecretRole(name='Secret Role 1', slug='secret-role-1'),
            SecretRole(name='Secret Role 2', slug='secret-role-2'),
        )
        SecretRole.objects.bulk_create(secretroles)

        # Create one secret per device to allow bulk-editing of names (which must be unique per device/role)
        Secret.objects.bulk_create((
            Secret(assigned_object=devices[0], role=secretroles[0], name='Secret 1', ciphertext=b'1234567890'),
            Secret(assigned_object=devices[1], role=secretroles[0], name='Secret 2', ciphertext=b'1234567890'),
            Secret(assigned_object=devices[2], role=secretroles[0], name='Secret 3', ciphertext=b'1234567890'),
        ))

        cls.form_data = {
            'assigned_object_type': 'dcim.device',
            'assigned_object_id': devices[1].pk,
            'role': secretroles[1].pk,
            'name': 'Secret X',
        }

        cls.bulk_edit_data = {
            'role': secretroles[1].pk,
            'name': 'New name',
        }

    def setUp(self):

        super().setUp()

        # Set up a master key for the test user
        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()
        master_key = userkey.get_master_key(PRIVATE_KEY)
        self.session_key = SessionKey(userkey=userkey)
        self.session_key.save(master_key)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_import_objects(self):
        self.add_permissions('secrets.add_secret')

        device = Device.objects.get(name='Device 1')
        csv_data = (
            "device,role,name,plaintext",
            f"{device.name},Secret Role 1,Secret 4,abcdefghij",
            f"{device.name},Secret Role 1,Secret 5,abcdefghij",
            f"{device.name},Secret Role 1,Secret 6,abcdefghij",
        )

        # Set the session_key cookie on the request
        session_key = base64.b64encode(self.session_key.key).decode('utf-8')
        self.client.cookies['session_key'] = session_key

        response = self.client.post(reverse('secrets:secret_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Secret.objects.count(), 6)
