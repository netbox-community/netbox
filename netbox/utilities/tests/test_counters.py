from django.test import TestCase
from dcim.models import *


class CountersTest(TestCase):
    """
    Validate the operation of dict_to_filter_params().
    """
    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestDevice1', site=site
        )
        device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='TestDevice2', site=site
        )

    def test_interface_count_addition(self):
        """
        When a new Cable is created, it must be cached on either termination point.
        """
        device1 = Device.objects.get(name='TestDevice1')
        device2 = Device.objects.get(name='TestDevice2')
        self.assertEqual(device1._interface_count, 0)
        self.assertEqual(device2._interface_count, 0)

        interface1 = Interface.objects.create(device=device1, name='eth0')
        interface2 = Interface.objects.create(device=device2, name='eth0')
        interface3 = Interface.objects.create(device=device2, name='eth1')
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1._interface_count, 1)
        self.assertEqual(device2._interface_count, 2)

    def test_interface_count_deletion(self):
        """
        When a Cable is deleted, the `cable` field on its termination points must be nullified. The str() method
        should still return the PK of the string even after being nullified.
        """
        device1 = Device.objects.get(name='TestDevice1')
        device2 = Device.objects.get(name='TestDevice2')
        self.assertEqual(device1._interface_count, 0)
        self.assertEqual(device2._interface_count, 0)

        interface1 = Interface.objects.create(device=device1, name='eth0')
        interface2 = Interface.objects.create(device=device2, name='eth0')
        interface3 = Interface.objects.create(device=device2, name='eth1')
        interface2.delete()
        interface3.delete()
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1._interface_count, 1)
        self.assertEqual(device2._interface_count, 0)
