from django.test import TestCase

from dcim.models import *
from utilities.testing.utils import create_test_device


class CountersTest(TestCase):
    """
    Validate the operation of dict_to_filter_params().
    """
    @classmethod
    def setUpTestData(cls):

        # Create devices
        device1 = create_test_device('Device 1')
        device2 = create_test_device('Device 2')

        # Create interfaces
        Interface.objects.create(device=device1, name='Interface 1')
        Interface.objects.create(device=device1, name='Interface 2')
        Interface.objects.create(device=device2, name='Interface 3')
        Interface.objects.create(device=device2, name='Interface 4')

    def test_interface_count_addition(self):
        """
        When a tracked object (Interface) is added the tracking counter should be updated.
        """
        device1, device2 = Device.objects.all()
        self.assertEqual(device1._interface_count, 2)
        self.assertEqual(device2._interface_count, 2)

        Interface.objects.create(device=device1, name='Interface 5')
        Interface.objects.create(device=device2, name='Interface 6')
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1._interface_count, 3)
        self.assertEqual(device2._interface_count, 3)

    def test_interface_count_deletion(self):
        """
        When a tracked object (Interface) is deleted the tracking counter should be updated.
        """
        device1, device2 = Device.objects.all()
        self.assertEqual(device1._interface_count, 2)
        self.assertEqual(device2._interface_count, 2)

        Interface.objects.get(name='Interface 1').delete()
        Interface.objects.get(name='Interface 3').delete()
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1._interface_count, 1)
        self.assertEqual(device2._interface_count, 1)
