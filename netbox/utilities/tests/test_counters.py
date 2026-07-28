from unittest.mock import patch

from django.urls import reverse

from dcim.models import *
from utilities.counters import connect_counters, update_counter
from utilities.testing.base import TestCase
from utilities.testing.utils import create_test_device


class CountersTestCase(TestCase):
    """
    Validate the operation of the CounterCacheField (tracking counters).
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
        When a tracked object (Interface) is added, the tracking counter should be updated.
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
        When a tracked object (Interface) is deleted, the tracking counter should be updated.
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

    def test_counter_skipped_when_parent_deleted(self):
        """
        Deleting a parent object should not issue a counter update for each cascaded child on that
        same parent (the row is being removed, so the UPDATE is a no-op). Counters on surviving
        related objects must still be updated.
        """
        device1 = Device.objects.get(name='Device 1')
        device_type = device1.device_type
        self.assertEqual(device_type.device_count, 2)

        # The Device must have tracked children for the suppression to be meaningful; otherwise the
        # assertions below would pass trivially with nothing to suppress
        self.assertEqual(device1.interfaces.count(), 2)

        # Wrap update_counter so the real counter logic still runs while we record each call
        with patch('utilities.counters.update_counter', wraps=update_counter) as mock_update:
            device1.delete()

        # The Device's own interface counter must not be updated per cascaded Interface, since the
        # Device is itself being deleted
        counter_names = [call.args[2] for call in mock_update.call_args_list]
        self.assertNotIn('interface_count', counter_names)

        # The counter on the surviving parent (DeviceType) must still be decremented
        self.assertIn('device_count', counter_names)
        device_type.refresh_from_db()
        self.assertEqual(device_type.device_count, 1)

        # Exactly one update should fire (DeviceType.device_count). Without the optimization the two
        # cascaded Interfaces on Device 1 would each have triggered an interface_count update.
        self.assertEqual(mock_update.call_count, 1)

    def test_counter_skipped_when_parent_deleted_via_queryset(self):
        """
        A bulk QuerySet delete (e.g. Device.objects.filter(...).delete(), as used by scripts,
        plugins, and programmatic callers) sets `origin` to the QuerySet rather than a single
        object. Counter updates for children whose parent belongs to that QuerySet must be
        suppressed, while counters on surviving related objects are still updated.
        """
        device1 = Device.objects.get(name='Device 1')
        device_type = device1.device_type
        self.assertEqual(device_type.device_count, 2)

        # The Device must have tracked children for the suppression to be meaningful
        self.assertEqual(device1.interfaces.count(), 2)

        # Wrap update_counter so the real counter logic still runs while we record each call
        with patch('utilities.counters.update_counter', wraps=update_counter) as mock_update:
            Device.objects.filter(name='Device 1').delete()

        # The deleted Device's interface_count must not be decremented per cascaded Interface, and
        # the only update should be the surviving DeviceType's device_count
        counter_names = [call.args[2] for call in mock_update.call_args_list]
        self.assertEqual(counter_names, ['device_count'])
        device_type.refresh_from_db()
        self.assertEqual(device_type.device_count, 1)

    def test_interface_count_move(self):
        """
        When a tracked object (Interface) is moved, the tracking counter should be updated.
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

    def test_mptt_child_delete(self):
        device1 = Device.objects.first()
        inventory_item1 = InventoryItem.objects.create(device=device1, name='Inventory Item 1')
        InventoryItem.objects.create(device=device1, name='Inventory Item 2', parent=inventory_item1)
        device1.refresh_from_db()
        self.assertEqual(device1.inventory_item_count, 2)

        # Setup bulk_delete for the inventory items
        self.add_permissions('dcim.view_inventoryitem', 'dcim.delete_inventoryitem')
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

    def test_signal_connections_are_idempotent_per_sender(self):
        """
        Calling connect_counters() again must not register duplicate receivers.
        Creating a device after repeated "connect_counters" should still yield +1.
        """
        connect_counters(DeviceType, VirtualChassis)
        vc, _ = VirtualChassis.objects.get_or_create(name='Virtual Chassis 1')
        device1, device2 = Device.objects.all()
        self.assertEqual(device1.device_type.device_count, 2)
        self.assertEqual(vc.member_count, 0)

        # Call again (should be a no-op for sender registrations)
        connect_counters(DeviceType, VirtualChassis)

        # Create one new device
        device3 = create_test_device('Device 3')
        device3.virtual_chassis = vc
        device3.save()

        # Ensure counter incremented correctly
        device1.refresh_from_db()
        vc.refresh_from_db()
        self.assertEqual(device1.device_type.device_count, 3, 'device_count should increment exactly once')
        self.assertEqual(vc.member_count, 1, 'member_count should increment exactly once')

        # Clean up and ensure counter decremented correctly
        device3.delete()
        device1.refresh_from_db()
        vc.refresh_from_db()
        self.assertEqual(device1.device_type.device_count, 2, 'device_count should decrement exactly once')
        self.assertEqual(vc.member_count, 0, 'member_count should decrement exactly once')
