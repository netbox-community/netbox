from django.test import override_settings
from django.urls import reverse

from dcim.models import *
from utilities.testing.base import TestCase
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

    def test_interface_count_creation(self):
        """
        When a tracked object (Interface) is added the tracking counter should be updated.
        """
        device1, device2 = Device.objects.all()
        self.assertEqual(device1.interface_count, 2)
        self.assertEqual(device2.interface_count, 2)

        interface1 = Interface.objects.create(device=device1, name='Interface 5')
        Interface.objects.create(device=device2, name='Interface 6')
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1.interface_count, 3)
        self.assertEqual(device2.interface_count, 3)

        # test saving an existing object - counter should not change
        interface1.save()
        device1.refresh_from_db()
        self.assertEqual(device1.interface_count, 3)

        # test save where tracked object FK back pointer is None
        vc = VirtualChassis.objects.create(name='Virtual Chassis 1')
        device1.virtual_chassis = vc
        device1.save()
        vc.refresh_from_db()
        self.assertEqual(vc.member_count, 1)

    def test_interface_count_deletion(self):
        """
        When a tracked object (Interface) is deleted the tracking counter should be updated.
        """
        device1, device2 = Device.objects.all()
        self.assertEqual(device1.interface_count, 2)
        self.assertEqual(device2.interface_count, 2)

        Interface.objects.get(name='Interface 1').delete()
        Interface.objects.get(name='Interface 3').delete()
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1.interface_count, 1)
        self.assertEqual(device2.interface_count, 1)

    def test_interface_count_move(self):
        """
        When a tracked object (Interface) is moved the tracking counter should be updated.
        """
        device1, device2 = Device.objects.all()
        self.assertEqual(device1.interface_count, 2)
        self.assertEqual(device2.interface_count, 2)

        interface1 = Interface.objects.get(name='Interface 1')
        interface1.device = device2
        interface1.save()

        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1.interface_count, 1)
        self.assertEqual(device2.interface_count, 3)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_mptt_child_delete(self):
        device1, device2 = Device.objects.all()
        inventory_item1 = InventoryItem.objects.create(device=device1, name='Inventory Item 1')
        InventoryItem.objects.create(device=device1, name='Inventory Item 2', parent=inventory_item1)
        device1.refresh_from_db()
        self.assertEqual(device1.inventory_item_count, 2)

        # Setup bulk_delete for the inventory items
        self.add_permissions('dcim.delete_inventoryitem')
        pk_list = device1.inventoryitems.values_list('pk', flat=True)
        data = {
            'pk': pk_list,
            'confirm': True,
            '_confirm': True,  # Form button
        }

        # Try POST with model-level permission
        self.client.post(reverse("dcim:inventoryitem_bulk_delete"), data)
        device1.refresh_from_db()
        self.assertEqual(device1.inventory_item_count, 0)
