from unittest.mock import patch

from django.db.utils import ConnectionDoesNotExist
from django.test import override_settings
from django.urls import reverse

from dcim.models import *
from utilities.counters import (
    connect_counters,
    post_delete_receiver,
    post_save_receiver,
    pre_delete_receiver,
    update_counter,
)
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


class UnpinnedQuery(Exception):
    """Raised when a query which should have been pinned to a connection is routed instead."""


class PinnedConnectionRouter:
    """
    Fails any read or write of the given models which is not pinned to an explicit database alias.
    Django consults DATABASE_ROUTERS only for queries which name no connection, so a signal handler
    which threads through the alias supplied by the signal never reaches this router. Each test
    leaves out the model being written, as Django routes that write itself.
    """
    def __init__(self, *models):
        self.models = models

    def _check(self, model, **hints):
        if model in self.models:
            raise UnpinnedQuery(f"{model.__name__} query was routed rather than pinned to a connection")

    db_for_read = _check
    db_for_write = _check


class CounterConnectionTestCase(TestCase):
    """
    Validate that the counter cache handlers issue their queries against the connection the
    triggering object was written to, rather than letting DATABASE_ROUTERS select one. A routed
    query updates a counter in a different database than the one holding the change which triggered
    it, leaving the cached count silently wrong.
    """
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')

    def test_create_pins_counter_increment(self):
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device)]):
            Interface.objects.create(device=self.device, name='Interface 1')

        self.device.refresh_from_db()
        self.assertEqual(self.device.interface_count, 1)

    def test_move_pins_both_counter_updates(self):
        other = create_test_device('Device 2')
        interface = Interface.objects.create(device=self.device, name='Interface 1')

        interface = Interface.objects.get(pk=interface.pk)
        interface.device = other
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device)]):
            interface.save()

        self.device.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.device.interface_count, 0)
        self.assertEqual(other.interface_count, 1)

    def test_receivers_use_the_alias_supplied_by_the_signal(self):
        """
        The tests above prove the queries name *an* alias, but with one configured database that
        alias is always 'default' — they would pass just as well against a hardcoded
        .using('default'). Invoking each receiver with an alias that does not exist distinguishes
        "threaded through from the signal" from "happens to be the default".
        """
        interface = Interface.objects.create(device=self.device, name='Interface 1')
        interface = Interface.objects.get(pk=interface.pk)

        with self.assertRaises(ConnectionDoesNotExist):
            post_save_receiver(Interface, interface, created=True, using='nonexistent')

        # origin=None: the parent is not itself being deleted, so the existence guard runs
        with self.assertRaises(ConnectionDoesNotExist):
            pre_delete_receiver(Interface, interface, origin=None, using='nonexistent')

        with self.assertRaises(ConnectionDoesNotExist):
            post_delete_receiver(Interface, interface, origin=None, using='nonexistent')

    def test_delete_pins_counter_decrement(self):
        interface = Interface.objects.create(device=self.device, name='Interface 1')
        self.device.refresh_from_db()
        self.assertEqual(self.device.interface_count, 1)

        # The delete itself is pinned, as Django routes an unpinned one; that leaves
        # pre_delete_receiver's existence guard as the only Interface query in scope, and that read
        # decides whether the decrement below happens at all.
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(Device, Interface)]):
            Interface.objects.using('default').filter(pk=interface.pk).delete()

        self.device.refresh_from_db()
        self.assertEqual(self.device.interface_count, 0)
