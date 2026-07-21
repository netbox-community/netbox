import signal
from contextlib import contextmanager
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, connection, router, transaction
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from circuits.models import Provider, ProviderNetwork, VirtualCircuit, VirtualCircuitTermination, VirtualCircuitType
from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices, ModuleStatusChoices, PortTypeChoices
from dcim.models import (
    Cable,
    Device,
    DeviceRole,
    DeviceType,
    FrontPort,
    FrontPortTemplate,
    Interface,
    InterfaceTemplate,
    InventoryItem,
    MACAddress,
    Manufacturer,
    Module,
    ModuleBay,
    ModuleBayTemplate,
    ModuleType,
    PortMapping,
    PortTemplateMapping,
    PowerOutlet,
    PowerOutletTemplate,
    PowerPort,
    PowerPortTemplate,
    RearPort,
    RearPortTemplate,
    Site,
    VirtualDeviceContext,
)
from dcim.models.module_moves import ModuleMovePlan
from dcim.utils import get_module_bay_positions, resolve_module_placeholder
from ipam.choices import FHRPGroupProtocolChoices
from ipam.models import VLAN, VRF, FHRPGroup, FHRPGroupAssignment, IPAddress, VLANTranslationPolicy
from utilities.exceptions import AbortRequest
from utilities.ordering import naturalize_interface
from utilities.testing import create_test_device
from vpn.choices import L2VPNTypeChoices, TunnelEncapsulationChoices
from vpn.models import L2VPN, L2VPNTermination, Tunnel, TunnelTermination
from wireless.models import WirelessLAN, WirelessLink


@contextmanager
def fail_after(seconds):
    """
    Fail the enclosed block if it runs longer than the given number of seconds. Backstop
    for the cycle-guard tests: a regressed hang fails one test fast instead of stalling the run.
    """
    def on_alarm(signum, frame):
        raise AssertionError(f'Operation did not complete within {seconds} seconds.')

    previous_handler = signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


class ModuleMoveValidationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device_a = create_test_device('Device A')
        cls.device_b = create_test_device('Device B')
        cls.bays_a = [
            ModuleBay.objects.create(device=cls.device_a, name=f'Bay A{i}') for i in range(1, 4)
        ]
        cls.bays_b = [
            ModuleBay.objects.create(device=cls.device_b, name=f'Bay B{i}') for i in range(1, 3)
        ]
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        cls.other_module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type N')
        cls.module = Module.objects.create(
            device=cls.device_a, module_bay=cls.bays_a[0], module_type=cls.module_type
        )

    def test_create_in_occupied_bay_fails(self):
        module = Module(device=self.device_a, module_bay=self.bays_a[0], module_type=self.module_type)
        with self.assertRaises(ValidationError) as cm:
            module.full_clean()
        self.assertIn('module_bay', cm.exception.message_dict)

    def test_move_to_occupied_bay_fails(self):
        occupant = Module.objects.create(
            device=self.device_a, module_bay=self.bays_a[1], module_type=self.module_type
        )
        self.module.module_bay = self.bays_a[1]
        with self.assertRaises(ValidationError) as cm:
            self.module.full_clean()
        self.assertIn('module_bay', cm.exception.message_dict)
        self.assertIn(str(occupant), str(cm.exception.message_dict['module_bay']))

    def test_move_to_own_bay_passes(self):
        self.module.serial = 'ABC123'
        self.module.full_clean()

    def test_move_to_other_device_bay_without_device_change_fails(self):
        # Existing device/bay consistency rule must keep rejecting a half-specified move
        self.module.module_bay = self.bays_b[0]
        with self.assertRaises(ValidationError):
            self.module.full_clean()

    def test_move_with_module_type_change_fails(self):
        self.module.module_bay = self.bays_a[1]
        self.module.module_type = self.other_module_type
        with self.assertRaises(ValidationError) as cm:
            self.module.full_clean()
        self.assertIn('module_type', cm.exception.message_dict)

    def test_module_type_change_without_move_passes(self):
        self.module.module_type = self.other_module_type
        self.module.full_clean()
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.module_type, self.other_module_type)


class ModuleSameDeviceMoveTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device A')
        cls.bay_a = ModuleBay.objects.create(device=cls.device, name='Bay A', position='A')
        cls.bay_b = ModuleBay.objects.create(device=cls.device, name='Bay B', position='B')
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        cls.module = Module.objects.create(
            device=cls.device, module_bay=cls.bay_a, module_type=cls.module_type
        )
        cls.interface = Interface.objects.create(
            device=cls.device, module=cls.module, name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.child_bay = ModuleBay.objects.create(
            device=cls.device, module=cls.module, name='Child Bay 1'
        )

    def test_move_to_empty_bay_updates_module_bay(self):
        self.module.module_bay = self.bay_b
        self.module.full_clean()
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.module_bay, self.bay_b)

    def test_move_reparents_direct_child_bays(self):
        self.module.module_bay = self.bay_b
        self.module.save()
        self.child_bay.refresh_from_db()
        self.assertEqual(self.child_bay.parent_id, self.bay_b.pk)
        self.assertTrue(str(self.child_bay.path).startswith(f'{self.bay_b.path}.'))

    def test_move_keeps_components_untouched_without_templates(self):
        self.module.module_bay = self.bay_b
        self.module.save()
        self.interface.refresh_from_db()
        self.assertEqual(self.interface.name, 'eth0')
        self.assertEqual(self.interface.device, self.device)

    def test_save_without_move_skips_planner(self):
        with patch('dcim.models.modules.ModuleMovePlan.from_module') as mock_plan:
            self.module.serial = 'XYZ789'
            self.module.save()
        mock_plan.assert_not_called()

    def test_save_level_move_with_type_change_raises_abort_request(self):
        other_type = ModuleType.objects.create(
            manufacturer=self.module_type.manufacturer, model='Module Type N'
        )
        self.module.module_bay = self.bay_b
        self.module.module_type = other_type
        with self.assertRaises(AbortRequest):
            self.module.save()


class ModuleSaveRoutingTestCase(TestCase):
    """Pins save() routing against concurrent, stale, deferred, and preset-pk instances."""

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.device = create_test_device('Device A')
        cls.device_b = create_test_device('Device B')
        cls.bay_a = ModuleBay.objects.create(device=cls.device, name='Bay A')
        cls.bay_b = ModuleBay.objects.create(device=cls.device, name='Bay B')
        cls.bay_c = ModuleBay.objects.create(device=cls.device_b, name='Bay C')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        InterfaceTemplate.objects.create(
            module_type=cls.module_type, name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        cls.module = Module.objects.create(
            device=cls.device, module_bay=cls.bay_a, module_type=cls.module_type
        )
        cls.child_bay = ModuleBay.objects.create(device=cls.device, module=cls.module, name='Child Bay 1')

    def _create_nested_subtree(self):
        child_module = Module(
            device=self.device,
            module_bay=self.child_bay,
            module_type=self.module_type,
        )
        child_module._disable_replication = True
        child_module.save()
        root_interface = Interface.objects.get(module=self.module, name='eth0')
        child_interface = Interface.objects.create(
            device=self.device,
            module=child_module,
            name='child0',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        return child_module, root_interface, child_interface

    @contextmanager
    def _move_to_other_device_before_locked_save(self):
        """Complete a competing move after save() routes the write but before the root lock."""
        original_save_existing = Module._save_existing
        moved = False

        def save_existing(instance, *args, **kwargs):
            nonlocal moved
            if not moved:
                moved = True
                concurrent = Module.objects.get(pk=self.module.pk)
                concurrent.device = self.device_b
                concurrent.module_bay = self.bay_c
                concurrent.save()
            return original_save_existing(instance, *args, **kwargs)

        with patch.object(Module, '_save_existing', autospec=True, side_effect=save_existing):
            yield

        self.assertTrue(moved)

    def test_plain_save_uses_locked_placement_for_routing(self):
        """A competing move landing before the root lock is resolved by the planner, not clobbered."""
        child_module, root_interface, child_interface = self._create_nested_subtree()
        stale = Module.objects.get(pk=self.module.pk)
        stale.comments = 'Stale session edit'

        with self._move_to_other_device_before_locked_save():
            stale.save()

        self.module.refresh_from_db()
        child_module.refresh_from_db()
        self.child_bay.refresh_from_db()
        root_interface.refresh_from_db()
        child_interface.refresh_from_db()
        self.assertEqual((self.module.device_id, self.module.module_bay_id), (self.device.pk, self.bay_a.pk))
        self.assertEqual(child_module.device_id, self.device.pk)
        self.assertEqual((self.child_bay.device_id, self.child_bay.parent_id), (self.device.pk, self.bay_a.pk))
        self.assertEqual(root_interface.device_id, self.device.pk)
        self.assertEqual(child_interface.device_id, self.device.pk)
        self.assertEqual(self.module.comments, 'Stale session edit')

    def test_update_fields_are_checked_against_locked_placement(self):
        """update_fields completeness is re-judged against the placement a competing move just committed."""
        child_module, root_interface, child_interface = self._create_nested_subtree()
        module = Module.objects.get(pk=self.module.pk)
        module.module_bay = self.bay_b

        with self._move_to_other_device_before_locked_save():
            with self.assertRaises(AbortRequest):
                module.save(update_fields=['module_bay'])

        self.module.refresh_from_db()
        child_module.refresh_from_db()
        self.child_bay.refresh_from_db()
        root_interface.refresh_from_db()
        child_interface.refresh_from_db()
        self.assertEqual((self.module.device_id, self.module.module_bay_id), (self.device_b.pk, self.bay_c.pk))
        self.assertEqual(child_module.device_id, self.device_b.pk)
        self.assertEqual((self.child_bay.device_id, self.child_bay.parent_id), (self.device_b.pk, self.bay_c.pk))
        self.assertEqual(root_interface.device_id, self.device_b.pk)
        self.assertEqual(child_interface.device_id, self.device_b.pk)

    def test_stale_instance_plain_save_after_move_keeps_children_consistent(self):
        instance_a = Module.objects.get(pk=self.module.pk)
        instance_b = Module.objects.get(pk=self.module.pk)
        instance_b.module_bay = self.bay_b
        instance_b.save()

        instance_a.comments = 'Stale session edit'
        instance_a.save()

        self.module.refresh_from_db()
        self.child_bay.refresh_from_db()
        self.assertEqual(self.module.comments, 'Stale session edit')
        self.assertEqual(self.child_bay.parent_id, self.module.module_bay_id)
        self.assertTrue(str(self.child_bay.path).startswith(f'{self.module.module_bay.path}.'))

    def test_deferred_device_field_save_with_update_fields_succeeds(self):
        module = Module.objects.defer('device').get(pk=self.module.pk)
        module.status = ModuleStatusChoices.STATUS_OFFLINE
        module.save(update_fields=['status'])
        module.refresh_from_db()
        self.assertEqual(module.status, ModuleStatusChoices.STATUS_OFFLINE)
        self.assertEqual(module.module_bay, self.bay_a)

    def test_out_of_band_placement_change_then_refresh_then_save_skips_planner(self):
        # Routing always enters the locked read; a refreshed instance shows no delta there, so no plan is built.
        Module.objects.filter(pk=self.module.pk).update(module_bay=self.bay_b)
        self.module.refresh_from_db()
        with patch.object(ModuleMovePlan, 'from_module') as mock_plan:
            self.module.serial = 'REFRESHED1'
            self.module.save()
        mock_plan.assert_not_called()
        self.module.refresh_from_db()
        self.assertEqual(self.module.serial, 'REFRESHED1')
        self.assertEqual(self.module.module_bay, self.bay_b)

    def test_preset_pk_save_with_unchanged_placement_does_not_replicate_components(self):
        interface_count_before = Interface.objects.filter(module=self.module).count()
        Module(
            pk=self.module.pk, device=self.module.device, module_bay=self.module.module_bay,
            module_type=self.module.module_type,
        ).save()
        self.assertEqual(Interface.objects.filter(module=self.module).count(), interface_count_before)

    def test_preset_unused_pk_save_creates_module(self):
        """A never-saved instance with an explicit unused pk is created, not treated as a move."""
        unused_pk = Module.objects.order_by('-pk').first().pk + 1000
        device = create_test_device('Device P')
        bay = ModuleBay.objects.create(device=device, name='Preset Bay')
        Module(pk=unused_pk, device=device, module_bay=bay, module_type=self.module_type).save()
        self.assertTrue(Module.objects.filter(pk=unused_pk).exists())
        self.assertTrue(Interface.objects.filter(module_id=unused_pk, name='eth0').exists())

    def test_pk_reassignment_clone_creates_new_module(self):
        """A fetched instance saved under a fresh unused pk creates a new row and keeps the original."""
        clone = Module.objects.get(pk=self.module.pk)
        device = create_test_device('Device C')
        bay = ModuleBay.objects.create(device=device, name='Clone Bay')
        clone.pk = Module.objects.order_by('-pk').first().pk + 1000
        clone.device = device
        clone.module_bay = bay
        clone.save()
        self.assertTrue(Module.objects.filter(pk=clone.pk).exists())
        self.assertTrue(Module.objects.filter(pk=self.module.pk).exists())

    def test_plain_save_after_concurrent_delete_recreates_module(self):
        """A stale full save whose row was deleted underneath falls through to create, like a plain Django save."""
        stale = Module.objects.get(pk=self.module.pk)
        Module.objects.filter(pk=stale.pk).delete()
        stale.comments = 'Recreated'
        stale.save()
        self.assertTrue(Module.objects.filter(pk=stale.pk, comments='Recreated').exists())

    def test_cross_device_stale_plain_save_moves_subtree_back_consistently(self):
        """
        A stale full save that reverts a committed cross-device move runs the planner,
        so the root module, child bays, and components land on one device together.
        """
        stale = Module.objects.get(pk=self.module.pk)

        mover = Module.objects.get(pk=self.module.pk)
        mover.device = self.device_b
        mover.module_bay = self.bay_c
        mover.save()

        stale.comments = 'Stale full save'
        stale.save()

        self.module.refresh_from_db()
        self.child_bay.refresh_from_db()
        interface = Interface.objects.get(module=self.module, name='eth0')
        self.assertEqual(self.module.comments, 'Stale full save')
        self.assertEqual(self.module.device, self.device)
        self.assertEqual(self.module.module_bay, self.bay_a)
        self.assertEqual(self.child_bay.device, self.device)
        self.assertEqual(self.child_bay.parent_id, self.bay_a.pk)
        self.assertEqual(interface.device, self.device)


class ModuleMoveRaceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device A')
        cls.bay_a = ModuleBay.objects.create(device=cls.device, name='Bay A')
        cls.bay_b = ModuleBay.objects.create(device=cls.device, name='Bay B')
        cls.bay_c = ModuleBay.objects.create(device=cls.device, name='Bay C')
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        cls.module_1 = Module.objects.create(
            device=cls.device, module_bay=cls.bay_a, module_type=cls.module_type
        )
        cls.module_2 = Module.objects.create(
            device=cls.device, module_bay=cls.bay_b, module_type=cls.module_type
        )

    def test_bulk_update_into_occupied_bay_hits_db_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Module.objects.filter(pk=self.module_2.pk).update(module_bay=self.bay_a)

    def test_locked_validation_catches_occupied_bay_bypassing_clean(self):
        # Simulate a TOCTOU window: clean() was never run (direct save), the target
        # bay is genuinely occupied, and the in-save locked validation must reject.
        self.module_2.module_bay = self.bay_a
        with self.assertRaises(AbortRequest):
            self.module_2.save()

    def test_move_into_own_subtree_bypassing_clean_is_rejected(self):
        child_bay = ModuleBay.objects.create(device=self.device, module=self.module_1, name='Child Bay 1')
        self.module_1.module_bay = child_bay
        with self.assertRaises(AbortRequest):
            self.module_1.save()

    def test_full_clean_on_cyclic_hierarchy_raises_validation_error_promptly(self):
        # A two-module cycle created via .update() (bypassing clean()) must raise promptly, not hang.
        child_bay_1 = ModuleBay.objects.create(device=self.device, module=self.module_1, name='Child Bay 1')
        child_bay_2 = ModuleBay.objects.create(device=self.device, module=self.module_2, name='Child Bay 2')
        Module.objects.filter(pk=self.module_1.pk).update(module_bay=child_bay_2)
        Module.objects.filter(pk=self.module_2.pk).update(module_bay=child_bay_1)
        module = Module.objects.get(pk=self.module_1.pk)
        module.module_bay = self.bay_c
        with fail_after(15):
            with self.assertRaises(ValidationError) as cm:
                module.full_clean()
        self.assertIn('module_bay', cm.exception.message_dict)
        self.assertIn('contains a cycle', str(cm.exception.message_dict['module_bay']))

    def test_move_into_cyclic_hierarchy_bypassing_clean_raises_abort_request(self):
        # Same cycle, reached via direct save() (clean() never runs); must abort, not hang.
        child_bay_1 = ModuleBay.objects.create(device=self.device, module=self.module_1, name='Child Bay 1')
        child_bay_2 = ModuleBay.objects.create(device=self.device, module=self.module_2, name='Child Bay 2')
        Module.objects.filter(pk=self.module_1.pk).update(module_bay=child_bay_2)
        Module.objects.filter(pk=self.module_2.pk).update(module_bay=child_bay_1)
        self.module_1.module_bay = self.bay_c
        with fail_after(15):
            with self.assertRaises(AbortRequest):
                self.module_1.save()

    def test_create_in_cyclic_hierarchy_with_token_template_raises_abort_request(self):
        # _save_new()'s template resolution walks the target bay's ancestry; a cycle must abort, not hang.
        child_bay_1 = ModuleBay.objects.create(device=self.device, module=self.module_1, name='Child Bay 1')
        child_bay_2 = ModuleBay.objects.create(device=self.device, module=self.module_2, name='Child Bay 2')
        Module.objects.filter(pk=self.module_1.pk).update(module_bay=child_bay_2)
        Module.objects.filter(pk=self.module_2.pk).update(module_bay=child_bay_1)
        token_type = ModuleType.objects.create(
            manufacturer=self.module_type.manufacturer, model='Module Type Token'
        )
        InterfaceTemplate.objects.create(
            module_type=token_type, name='eth{module}/0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        target_bay = ModuleBay.objects.create(
            device=self.device, module=self.module_1, name='Child Bay 3', position='3'
        )
        # Fresh fetch so the ancestry walk reads database state, not cached relations
        target_bay = ModuleBay.objects.get(pk=target_bay.pk)
        module = Module(device=self.device, module_bay=target_bay, module_type=token_type)
        with fail_after(15):
            with self.assertRaises(AbortRequest) as cm:
                module.save()
        self.assertIn('contains a cycle', cm.exception.message)

    def test_lock_rediscovers_membership_added_after_planning(self):
        old = Module.objects.get(pk=self.module_1.pk)
        new = Module.objects.get(pk=self.module_1.pk)
        new.module_bay = ModuleBay.objects.create(device=self.device, name='Bay C')
        plan = ModuleMovePlan.from_module(old_module=old, new_module=new)
        late_interface = Interface.objects.create(
            device=self.device, module=self.module_1, name='late0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        with transaction.atomic():
            plan.lock()
        self.assertIn(late_interface.pk, [obj.pk for obj in plan.components[Interface]])

    def test_locked_device_get_does_not_exist_raises_abort_request(self):
        # Same TOCTOU, at the device row lock acquired by ModuleMovePlan.lock(): the
        # single-statement filter(pk__in=...) form returns fewer rows than expected pks.
        self.module_1.module_bay = self.bay_c
        with patch.object(Device.objects, 'select_for_update') as mock_sfu:
            mock_sfu.return_value.filter.return_value.order_by.return_value = []
            with self.assertRaises(AbortRequest):
                self.module_1.save()


class ModuleMoveSaveContractTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device A')
        cls.bay_a = ModuleBay.objects.create(device=cls.device, name='Bay A')
        cls.bay_b = ModuleBay.objects.create(device=cls.device, name='Bay B')
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        cls.module = Module.objects.create(
            device=cls.device, module_bay=cls.bay_a, module_type=cls.module_type
        )

    def test_update_fields_excluding_module_bay_saves_without_moving(self):
        # A changed placement field left out of update_fields is never persisted, so no move happens.
        self.module.module_bay = self.bay_b
        self.module.serial = 'ABC123'
        self.module.save(update_fields=['serial'])
        self.module.refresh_from_db()
        self.assertEqual(self.module.serial, 'ABC123')
        self.assertEqual(self.module.module_bay, self.bay_a)

    def test_update_fields_including_placement_moves(self):
        self.module.module_bay = self.bay_b
        self.module.save(update_fields=['device', 'module_bay'])
        self.module.refresh_from_db()
        self.assertEqual(self.module.module_bay, self.bay_b)

    def test_deadlock_is_translated_to_abort_request(self):
        deadlock = OperationalError('Simulated deadlock error')
        deadlock.__cause__ = type('FakeDeadlock', (Exception,), {'sqlstate': '40P01'})()
        self.module.module_bay = self.bay_b
        with patch.object(ModuleMovePlan, 'lock', side_effect=deadlock):
            with self.assertRaises(AbortRequest):
                self.module.save()

    def test_non_deadlock_operational_error_propagates(self):
        error = OperationalError('Simulated connection error')
        self.module.module_bay = self.bay_b
        with patch.object(ModuleMovePlan, 'lock', side_effect=error):
            with self.assertRaises(OperationalError):
                self.module.save()

    def test_post_save_signals_use_write_alias(self):
        ModuleBay.objects.create(device=self.device, module=self.module, name='Child Bay 1')
        self.module.module_bay = self.bay_b
        with patch('dcim.models.module_moves.post_save') as mock_signal:
            self.module.save()
        self.assertTrue(mock_signal.send.called)
        for call in mock_signal.send.call_args_list:
            self.assertEqual(call.kwargs['using'], router.db_for_write(ModuleBay))

    def test_move_to_deleted_bay_raises_abort_request(self):
        target = ModuleBay.objects.create(device=self.device, name='Bay C')
        self.module.module_bay = target
        ModuleBay.objects.filter(pk=target.pk).delete()
        with self.assertRaises(AbortRequest):
            self.module.save()

    def test_partial_update_fields_after_completed_move_succeeds(self):
        self.module.module_bay = self.bay_b
        self.module.save()
        self.module.serial = 'A1'
        self.module.save(update_fields=['serial'])
        self.module.refresh_from_db()
        self.assertEqual(self.module.serial, 'A1')
        self.assertEqual(self.module.module_bay, self.bay_b)

    def test_update_fields_with_module_bay_name_moves_same_device(self):
        child_bay = ModuleBay.objects.create(device=self.device, module=self.module, name='Child Bay 1')
        self.module.module_bay = self.bay_b
        self.module.save(update_fields=['module_bay'])
        self.module.refresh_from_db()
        child_bay.refresh_from_db()
        self.assertEqual(self.module.module_bay, self.bay_b)
        self.assertEqual(child_bay.parent_id, self.bay_b.pk)

    def test_update_fields_with_attnames_moves_cross_device(self):
        device_b = create_test_device('Device B')
        bay_c = ModuleBay.objects.create(device=device_b, name='Bay C')
        self.module.device = device_b
        self.module.module_bay = bay_c
        self.module.save(update_fields=['device_id', 'module_bay_id'])
        self.module.refresh_from_db()
        self.assertEqual(self.module.device, device_b)
        self.assertEqual(self.module.module_bay, bay_c)

    def test_update_fields_missing_device_rejects_cross_device_delta(self):
        device_b = create_test_device('Device B')
        bay_c = ModuleBay.objects.create(device=device_b, name='Bay C')
        self.module.device = device_b
        self.module.module_bay = bay_c
        with self.assertRaises(AbortRequest):
            self.module.save(update_fields=['module_bay'])

    def test_update_fields_incomplete_against_current_placement_rejects(self):
        """
        update_fields completeness is judged against the locked database placement,
        not the placement the saving instance last observed.
        """
        device_b = create_test_device('Device B')
        bay_c = ModuleBay.objects.create(device=device_b, name='Bay C')
        stale = Module.objects.get(pk=self.module.pk)

        mover = Module.objects.get(pk=self.module.pk)
        mover.device = device_b
        mover.module_bay = bay_c
        mover.save()

        stale.module_bay = self.bay_b
        with self.assertRaises(AbortRequest):
            stale.save(update_fields=['module_bay'])
        self.module.refresh_from_db()
        self.assertEqual(self.module.device, device_b)
        self.assertEqual(self.module.module_bay, bay_c)

    def test_update_fields_with_unchanged_placement_field_saves_without_moving(self):
        """
        A placement field listed in update_fields with an unchanged value is written as-is;
        a diverged placement field left out of update_fields never triggers a move.
        """
        self.module.module_bay = self.bay_b
        self.module.serial = 'NOMOVE1'
        with patch.object(ModuleMovePlan, 'from_module') as mock_plan:
            self.module.save(update_fields=['device', 'serial'])
        mock_plan.assert_not_called()
        self.module.refresh_from_db()
        self.assertEqual(self.module.serial, 'NOMOVE1')
        self.assertEqual(self.module.module_bay, self.bay_a)


class ModuleMoveRenameTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        role = DeviceRole.objects.create(name='Role 1', slug='role-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Chassis', slug='chassis')
        ModuleBayTemplate.objects.create(device_type=device_type, name='Slot 1', position='1')
        ModuleBayTemplate.objects.create(device_type=device_type, name='Slot 2', position='2')

        cls.line_card_type = ModuleType.objects.create(manufacturer=manufacturer, model='Line Card')
        InterfaceTemplate.objects.create(
            module_type=cls.line_card_type,
            name='Ethernet{module}/1',
            label='Port {module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        ModuleBayTemplate.objects.create(
            module_type=cls.line_card_type, name='SFP bay {module}/1', position='{module}/1'
        )

        cls.sfp_type = ModuleType.objects.create(manufacturer=manufacturer, model='SFP')
        InterfaceTemplate.objects.create(
            module_type=cls.sfp_type, name='SFP {module}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        cls.device = Device.objects.create(name='Chassis A', device_type=device_type, role=role, site=site)
        cls.slot_1 = cls.device.modulebays.get(name='Slot 1')
        cls.slot_2 = cls.device.modulebays.get(name='Slot 2')
        cls.line_card = Module.objects.create(
            device=cls.device, module_bay=cls.slot_1, module_type=cls.line_card_type
        )
        cls.sfp_bay = cls.line_card.modulebays.get(name='SFP bay 1/1')
        cls.sfp_module = Module.objects.create(
            device=cls.device, module_bay=cls.sfp_bay, module_type=cls.sfp_type
        )

    def _move_line_card_to_slot_2(self):
        self.line_card.module_bay = self.slot_2
        self.line_card.full_clean()
        self.line_card.save()

    def test_same_device_move_renames_templated_interface(self):
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        self._move_line_card_to_slot_2()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'Ethernet2/1')
        self.assertEqual(interface.label, 'Port 2')
        self.assertEqual(interface._name, naturalize_interface('Ethernet2/1', max_length=100))

    def test_move_renames_nested_bay_and_grandchild_components(self):
        sfp_interface = self.sfp_module.interfaces.get(name='SFP 1/1')
        self._move_line_card_to_slot_2()
        self.sfp_bay.refresh_from_db()
        self.assertEqual(self.sfp_bay.name, 'SFP bay 2/1')
        self.assertEqual(self.sfp_bay.position, '2/1')
        sfp_interface.refresh_from_db()
        self.assertEqual(sfp_interface.name, 'SFP 2/1')

    def test_manually_renamed_component_is_preserved(self):
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        interface.name = 'uplink-core'
        interface.save()
        self._move_line_card_to_slot_2()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'uplink-core')

    def test_manually_changed_label_is_preserved_while_name_renames(self):
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        interface.label = 'Uplink'
        interface.save()
        self._move_line_card_to_slot_2()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'Ethernet2/1')
        self.assertEqual(interface.label, 'Uplink')

    def test_ambiguous_template_match_is_preserved(self):
        # A second template resolving to the same old name makes the match ambiguous
        InterfaceTemplate.objects.create(
            module_type=self.line_card_type, name='Ethernet1/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        self._move_line_card_to_slot_2()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'Ethernet1/1')

    def test_move_after_module_type_change_preserves_names(self):
        other_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Other Card'
        )
        self.line_card.module_type = other_type
        self.line_card.save()
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        self._move_line_card_to_slot_2()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'Ethernet1/1')

    def test_manually_changed_bay_position_stops_rename_cascade(self):
        self.sfp_bay.position = 'X'
        self.sfp_bay.save()
        sfp_interface = self.sfp_module.interfaces.get(name='SFP 1/1')
        self._move_line_card_to_slot_2()
        self.sfp_bay.refresh_from_db()
        self.assertEqual(self.sfp_bay.position, 'X')
        sfp_interface.refresh_from_db()
        self.assertEqual(sfp_interface.name, 'SFP 1/1')

    def test_duplicate_final_names_within_moved_set_fail(self):
        Interface.objects.create(
            device=self.device, module=self.line_card, name='Ethernet2/1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        self.line_card.module_bay = self.slot_2
        with self.assertRaises(ValidationError):
            self.line_card.full_clean()

    def test_conflict_with_existing_destination_component_fails(self):
        Interface.objects.create(
            device=self.device, name='Ethernet2/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        self.line_card.module_bay = self.slot_2
        with self.assertRaises(ValidationError):
            self.line_card.full_clean()

    def test_rename_chain_collision_is_rejected(self):
        # 'E{module}/1' resolves to E1/1 in slot 1 and E2/1 in slot 2, while 'E2/{module}'
        # resolves to E2/1 in slot 1 and E2/2 in slot 2: E1/1 -> E2/1 while E2/1 -> E2/2.
        # Applying both renames on the same device in one statement is order-dependent.
        InterfaceTemplate.objects.create(
            module_type=self.line_card_type, name='E2/{module}', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        InterfaceTemplate.objects.create(
            module_type=self.line_card_type, name='E{module}/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        Interface.objects.create(
            device=self.device, module=self.line_card, name='E2/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        Interface.objects.create(
            device=self.device, module=self.line_card, name='E1/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        self.line_card.module_bay = self.slot_2
        with self.assertRaises(ValidationError) as cm:
            self.line_card.full_clean()
        self.assertIn('current name of another moved', str(cm.exception))

    def test_bay_rename_chain_collision_is_rejected(self):
        # 'Bay E2/{module}' resolves to Bay E2/1 in slot 1 and Bay E2/2 in slot 2, while
        # 'Bay E{module}/1' resolves to Bay E1/1 in slot 1 and Bay E2/1 in slot 2: Bay E1/1
        # -> Bay E2/1 while Bay E2/1 -> Bay E2/2. Applying both renames in one same-device
        # bulk statement would collide on the destination namespace depending on row order.
        ModuleBayTemplate.objects.create(module_type=self.line_card_type, name='Bay E2/{module}')
        ModuleBayTemplate.objects.create(module_type=self.line_card_type, name='Bay E{module}/1')
        ModuleBay.objects.create(device=self.device, module=self.line_card, name='Bay E2/1')
        ModuleBay.objects.create(device=self.device, module=self.line_card, name='Bay E1/1')
        self.line_card.module_bay = self.slot_2
        with self.assertRaises(ValidationError) as cm:
            self.line_card.full_clean()
        self.assertIn('current name of another moved module bay', str(cm.exception))

    def test_rename_exceeding_name_max_length_is_rejected(self):
        name_limit = Interface._meta.get_field('name').max_length
        template_name_limit = InterfaceTemplate._meta.get_field('name').max_length
        position_limit = ModuleBay._meta.get_field('position').max_length
        prefix = 'A' * (template_name_limit - len('{module}'))
        long_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Oversized Name Card'
        )
        InterfaceTemplate.objects.create(
            module_type=long_type, name=f'{prefix}{{module}}', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        long_bay = ModuleBay.objects.create(device=self.device, name='Long Bay', position='X' * position_limit)
        module = Module.objects.create(device=self.device, module_bay=self.slot_2, module_type=long_type)
        interface = module.interfaces.get()
        self.assertLessEqual(len(interface.name), name_limit)

        module.module_bay = long_bay
        with self.assertRaises(ValidationError) as cm:
            module.full_clean()
        self.assertIn(str(interface), str(cm.exception))

    def test_rename_exceeding_position_max_length_is_rejected(self):
        position_limit = ModuleBay._meta.get_field('position').max_length
        template_position_limit = ModuleBayTemplate._meta.get_field('position').max_length
        prefix = 'B' * (template_position_limit - len('{module}'))
        long_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Oversized Position Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=long_type, name='Nested Bay {module}', position=f'{prefix}{{module}}'
        )
        long_bay = ModuleBay.objects.create(device=self.device, name='Long Bay', position='Y' * position_limit)
        module = Module.objects.create(device=self.device, module_bay=self.slot_2, module_type=long_type)
        bay = module.modulebays.get()

        module.module_bay = long_bay
        with self.assertRaises(ValidationError) as cm:
            module.full_clean()
        self.assertIn(str(bay), str(cm.exception))

    def test_leaf_token_left_raw_matches_fresh_walker_resolution(self):
        # A bay whose stored position literally contains an unresolved {module} token
        # (bypassing normal template-driven creation) must resolve its own children's
        # names identically to a fresh get_module_bay_positions() call, both before and
        # after a move, so a later move can still recognize the template match.
        odd_bay = ModuleBay.objects.create(
            device=self.device, module=self.line_card, name='Odd Bay', position='{module}A'
        )
        child_module = Module.objects.create(device=self.device, module_bay=odd_bay, module_type=self.sfp_type)
        child_interface = child_module.interfaces.get()

        self._move_line_card_to_slot_2()
        child_interface.refresh_from_db()
        odd_bay.refresh_from_db()
        expected_name = resolve_module_placeholder('SFP {module}', get_module_bay_positions(odd_bay))
        self.assertEqual(child_interface.name, expected_name)

    def test_second_move_still_renames_child_of_raw_token_bay(self):
        # Regression pin: a second move of the same module must still template-match and
        # rename a child nested under a raw-token bay, not silently stop renaming.
        two_token_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Two Token SFP'
        )
        InterfaceTemplate.objects.create(
            module_type=two_token_type, name='SFP {module}/{module}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        odd_bay = ModuleBay.objects.create(
            device=self.device, module=self.line_card, name='Odd Bay', position='{module}A'
        )
        child_module = Module.objects.create(device=self.device, module_bay=odd_bay, module_type=two_token_type)
        child_interface = child_module.interfaces.get()
        self.assertEqual(child_interface.name, 'SFP 1/{module}A')

        self._move_line_card_to_slot_2()
        child_interface.refresh_from_db()
        self.assertEqual(child_interface.name, 'SFP 2/{module}A')

        self.line_card.module_bay = self.slot_1
        self.line_card.full_clean()
        self.line_card.save()
        child_interface.refresh_from_db()
        self.assertEqual(child_interface.name, 'SFP 1/{module}A')

    def test_move_into_raw_token_bay_resolves_ancestor_from_child(self):
        """
        A raw {module} token on the DESTINATION bay resolves from the planned child
        position below it, matching a fresh post-move walker resolution exactly.
        """
        raw_slot = ModuleBay.objects.create(device=self.device, name='Raw Slot', position='{module}R')
        b_bay = ModuleBay.objects.create(device=self.device, module=self.line_card, name='B Bay', position='B')
        two_token_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Two Token'
        )
        InterfaceTemplate.objects.create(
            module_type=two_token_type, name='SFP {module}/{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
        )
        child_module = Module.objects.create(
            device=self.device, module_bay=b_bay, module_type=two_token_type
        )
        child_interface = child_module.interfaces.get(name='SFP 1/B')

        self.line_card.module_bay = raw_slot
        self.line_card.full_clean()
        self.line_card.save()

        child_interface.refresh_from_db()
        self.assertEqual(child_interface.name, 'SFP BR/B')
        self.assertNotIn('{module}', child_interface.name)
        fresh_chain = get_module_bay_positions(ModuleBay.objects.get(pk=b_bay.pk))
        self.assertEqual(child_interface.name, resolve_module_placeholder('SFP {module}/{module}', fresh_chain))
        # Leaf-raw parity: the moved module's own component sees the destination
        # bay's token unresolved, exactly as an install into that bay would
        root_interface = self.line_card.interfaces.get(name__startswith='Ethernet')
        self.assertEqual(root_interface.name, 'Ethernet{module}R/1')

    def test_move_under_multiple_raw_token_ancestors_resolves_full_chain(self):
        """
        Every ancestor level carrying a raw {module} token inherits from the resolved
        position below it, across more than one level.
        """
        bare_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Bare Carrier'
        )
        three_token_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Three Token'
        )
        InterfaceTemplate.objects.create(
            module_type=three_token_type, name='T{module}.{module}.{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        # Source: depth-3 chain ['7', '8', 'B'] so the three-token template resolves
        s1 = ModuleBay.objects.create(device=self.device, name='S1', position='7')
        mid_src = Module.objects.create(device=self.device, module_bay=s1, module_type=bare_type)
        s2 = ModuleBay.objects.create(device=self.device, module=mid_src, name='S2', position='8')
        carrier = Module.objects.create(device=self.device, module_bay=s2, module_type=bare_type)
        c_bay = ModuleBay.objects.create(device=self.device, module=carrier, name='C Bay', position='B')
        child_module = Module.objects.create(
            device=self.device, module_bay=c_bay, module_type=three_token_type
        )
        child_interface = child_module.interfaces.get(name='T7.8.B')
        # Destination: two stacked raw-token ancestors
        g_bay = ModuleBay.objects.create(device=self.device, name='G Bay', position='{module}X')
        mid_dst = Module.objects.create(device=self.device, module_bay=g_bay, module_type=bare_type)
        r_bay = ModuleBay.objects.create(device=self.device, module=mid_dst, name='R Bay', position='{module}R')

        carrier.module_bay = r_bay
        carrier.full_clean()
        carrier.save()

        child_interface.refresh_from_db()
        self.assertEqual(child_interface.name, 'TBRX.BR.B')
        self.assertNotIn('{module}', child_interface.name)
        fresh_chain = get_module_bay_positions(ModuleBay.objects.get(pk=c_bay.pk))
        self.assertEqual(fresh_chain, ['BRX', 'BR', 'B'])
        self.assertEqual(
            child_interface.name, resolve_module_placeholder('T{module}.{module}.{module}', fresh_chain)
        )

    def test_move_to_shallower_bay_with_unresolvable_template_is_rejected(self):
        """
        A component whose name matched a source template that cannot resolve at the
        destination depth rejects the move instead of silently keeping the stale name.
        """
        two_token_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Two Token'
        )
        InterfaceTemplate.objects.create(
            module_type=two_token_type, name='SFP {module}/{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
        )
        b_bay = ModuleBay.objects.create(device=self.device, module=self.line_card, name='B Bay', position='B')
        child_module = Module.objects.create(
            device=self.device, module_bay=b_bay, module_type=two_token_type
        )
        shallow = ModuleBay.objects.create(device=self.device, name='Shallow', position='X')

        child_module.module_bay = shallow
        with self.assertRaises(ValidationError) as cm:
            child_module.full_clean()
        self.assertIn('cannot be resolved', str(cm.exception))
        with self.assertRaises(AbortRequest):
            child_module.save()
        child_module.refresh_from_db()
        self.assertEqual(child_module.module_bay_id, b_bay.pk)
        self.assertTrue(child_module.interfaces.filter(name='SFP 1/B').exists())

    def test_matched_label_unresolvable_at_destination_rejects_move(self):
        """
        A label matching its source template resolution rejects the move when the
        label template cannot resolve at the destination depth.
        """
        label_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Label Type'
        )
        InterfaceTemplate.objects.create(
            module_type=label_type, name='N{module}', label='L{module}/{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        b_bay = ModuleBay.objects.create(device=self.device, module=self.line_card, name='B Bay', position='B')
        child_module = Module.objects.create(device=self.device, module_bay=b_bay, module_type=label_type)
        interface = child_module.interfaces.get(name='NB')
        self.assertEqual(interface.label, 'L1/B')
        shallow = ModuleBay.objects.create(device=self.device, name='Shallow', position='X')

        child_module.module_bay = shallow
        with self.assertRaises(ValidationError):
            child_module.full_clean()

    def test_unmatched_label_with_unresolvable_template_still_moves(self):
        """
        A manually customized label never source-matches, so an unresolvable label
        template does not block the move and the label is preserved.
        """
        label_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Label Type'
        )
        InterfaceTemplate.objects.create(
            module_type=label_type, name='N{module}', label='L{module}/{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        b_bay = ModuleBay.objects.create(device=self.device, module=self.line_card, name='B Bay', position='B')
        child_module = Module.objects.create(device=self.device, module_bay=b_bay, module_type=label_type)
        interface = child_module.interfaces.get(name='NB')
        interface.label = 'Custom'
        interface.save()
        shallow = ModuleBay.objects.create(device=self.device, name='Shallow', position='X')

        child_module.module_bay = shallow
        child_module.full_clean()
        child_module.save()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'NX')
        self.assertEqual(interface.label, 'Custom')

    def test_matched_bay_position_unresolvable_at_destination_rejects_move(self):
        """
        A module bay position matching its source template resolution rejects the move
        when the position template cannot resolve at the destination depth.
        """
        pos_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Pos Type'
        )
        ModuleBayTemplate.objects.create(module_type=pos_type, name='PB', position='{module}/{module}')
        b_bay = ModuleBay.objects.create(device=self.device, module=self.line_card, name='B Bay', position='B')
        pos_module = Module.objects.create(device=self.device, module_bay=b_bay, module_type=pos_type)
        self.assertEqual(pos_module.modulebays.get(name='PB').position, '1/B')
        shallow = ModuleBay.objects.create(device=self.device, name='Shallow', position='X')

        pos_module.module_bay = shallow
        with self.assertRaises(ValidationError):
            pos_module.full_clean()


class ModuleCrossDeviceBlockerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device_a = create_test_device('Device A')
        cls.device_b = create_test_device('Device B')
        cls.bay_a = ModuleBay.objects.create(device=cls.device_a, name='Bay A')
        cls.bay_b = ModuleBay.objects.create(device=cls.device_b, name='Bay B')
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        cls.module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type M')
        cls.module = Module.objects.create(
            device=cls.device_a, module_bay=cls.bay_a, module_type=cls.module_type
        )
        cls.interface = Interface.objects.create(
            device=cls.device_a, module=cls.module, name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

    def _assert_move_blocked(self, token):
        self.module.device = self.device_b
        self.module.module_bay = self.bay_b
        with self.assertRaises(ValidationError) as cm:
            self.module.full_clean()
        self.assertIn('cannot be moved to a different device', str(cm.exception))
        self.assertIn(token, str(cm.exception))

    def _assert_move_allowed(self):
        self.module.device = self.device_b
        self.module.module_bay = self.bay_b
        self.module.full_clean()

    def test_cable_blocks(self):
        peer = Interface.objects.create(
            device=self.device_a, name='peer0', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        Cable(a_terminations=[self.interface], b_terminations=[peer]).save()
        self._assert_move_blocked('cabled')

    def test_mark_connected_blocks(self):
        self.interface.mark_connected = True
        self.interface.save()
        self._assert_move_blocked('cabled or connection-marked')

    def test_ip_address_blocks(self):
        IPAddress.objects.create(address='192.0.2.1/32', assigned_object=self.interface)
        self._assert_move_blocked('IP addresses')

    def test_fhrp_group_assignment_blocks(self):
        group = FHRPGroup.objects.create(protocol=FHRPGroupProtocolChoices.PROTOCOL_VRRP2, group_id=1)
        FHRPGroupAssignment.objects.create(group=group, interface=self.interface, priority=100)
        self._assert_move_blocked('FHRP')

    def test_tunnel_termination_blocks(self):
        tunnel = Tunnel.objects.create(name='Tunnel 1', encapsulation=TunnelEncapsulationChoices.ENCAP_IP_IP)
        TunnelTermination.objects.create(tunnel=tunnel, termination=self.interface)
        self._assert_move_blocked('tunnel')

    def test_l2vpn_termination_blocks(self):
        l2vpn = L2VPN.objects.create(name='L2VPN 1', slug='l2vpn-1', type=L2VPNTypeChoices.TYPE_VXLAN)
        L2VPNTermination.objects.create(l2vpn=l2vpn, assigned_object=self.interface)
        self._assert_move_blocked('L2VPN')

    def test_virtual_circuit_termination_blocks(self):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(provider=provider, name='Provider Network 1')
        vc_type = VirtualCircuitType.objects.create(name='VC Type 1', slug='vc-type-1')
        vc = VirtualCircuit.objects.create(provider_network=provider_network, cid='VC 1', type=vc_type)
        virtual_interface = Interface.objects.create(
            device=self.device_a, module=self.module, name='vc0', type=InterfaceTypeChoices.TYPE_VIRTUAL
        )
        VirtualCircuitTermination.objects.create(virtual_circuit=vc, interface=virtual_interface)
        self._assert_move_blocked('virtual circuit')

    def test_wireless_link_blocks(self):
        radio_a = Interface.objects.create(
            device=self.device_a, module=self.module, name='radio0', type=InterfaceTypeChoices.TYPE_80211AC
        )
        radio_b = Interface.objects.create(
            device=self.device_a, name='radio1', type=InterfaceTypeChoices.TYPE_80211AC
        )
        WirelessLink(interface_a=radio_a, interface_b=radio_b, ssid='LINK1').save()
        self._assert_move_blocked('wireless links')

    def test_wireless_lan_blocks(self):
        wlan = WirelessLAN.objects.create(ssid='SSID1')
        self.interface.wireless_lans.add(wlan)
        self._assert_move_blocked('wireless LAN')

    def test_untagged_vlan_blocks(self):
        vlan = VLAN.objects.create(vid=100, name='VLAN 100')
        self.interface.mode = InterfaceModeChoices.MODE_ACCESS
        self.interface.untagged_vlan = vlan
        self.interface.save()
        self._assert_move_blocked('untagged VLAN')

    def test_tagged_vlan_blocks(self):
        vlan = VLAN.objects.create(vid=200, name='VLAN 200')
        self.interface.mode = InterfaceModeChoices.MODE_TAGGED
        self.interface.save()
        self.interface.tagged_vlans.add(vlan)
        self._assert_move_blocked('tagged VLANs')

    def test_qinq_svlan_blocks(self):
        svlan = VLAN.objects.create(vid=999, name='SVLAN 999')
        self.interface.mode = InterfaceModeChoices.MODE_Q_IN_Q
        self.interface.qinq_svlan = svlan
        self.interface.save()
        self._assert_move_blocked('Q-in-Q')

    def test_vlan_translation_policy_blocks(self):
        policy = VLANTranslationPolicy.objects.create(name='Policy 1')
        self.interface.vlan_translation_policy = policy
        self.interface.save()
        self._assert_move_blocked('VLAN translation')

    def test_vdc_assignment_blocks(self):
        vdc = VirtualDeviceContext.objects.create(device=self.device_a, name='VDC 1', status='active')
        self.interface.vdcs.add(vdc)
        self._assert_move_blocked('VDC')

    def test_vrf_blocks(self):
        vrf = VRF.objects.create(name='VRF 1')
        self.interface.vrf = vrf
        self.interface.save()
        self._assert_move_blocked('VRF')

    def test_parent_outside_moved_set_blocks(self):
        parent = Interface.objects.create(
            device=self.device_a, name='parent0', type=InterfaceTypeChoices.TYPE_VIRTUAL
        )
        Interface.objects.create(
            device=self.device_a, module=self.module, name='child0',
            type=InterfaceTypeChoices.TYPE_VIRTUAL, parent=parent,
        )
        self._assert_move_blocked('boundary')

    def test_bridge_outside_moved_set_blocks(self):
        bridge = Interface.objects.create(
            device=self.device_a, name='bridge0', type=InterfaceTypeChoices.TYPE_BRIDGE
        )
        self.interface.bridge = bridge
        self.interface.save()
        self._assert_move_blocked('boundary')

    def test_lag_outside_moved_set_blocks(self):
        lag = Interface.objects.create(
            device=self.device_a, name='lag0', type=InterfaceTypeChoices.TYPE_LAG
        )
        self.interface.lag = lag
        self.interface.save()
        self._assert_move_blocked('boundary')

    def test_nonmoved_member_of_moved_lag_blocks(self):
        lag = Interface.objects.create(
            device=self.device_a, module=self.module, name='lag0', type=InterfaceTypeChoices.TYPE_LAG
        )
        Interface.objects.create(
            device=self.device_a, name='member0', type=InterfaceTypeChoices.TYPE_1GE_FIXED, lag=lag
        )
        self._assert_move_blocked('boundary')

    def test_split_port_mapping_blocks(self):
        front_port = FrontPort.objects.create(
            device=self.device_a, module=self.module, name='Front 1', type=PortTypeChoices.TYPE_LC
        )
        rear_port = RearPort.objects.create(
            device=self.device_a, name='Rear 1', type=PortTypeChoices.TYPE_LC, positions=1
        )
        PortMapping.objects.create(
            front_port=front_port, front_port_position=1, rear_port=rear_port, rear_port_position=1
        )
        self._assert_move_blocked('port mappings')

    def test_split_power_outlet_blocks(self):
        power_port = PowerPort.objects.create(device=self.device_a, name='PP 1')
        PowerOutlet.objects.create(
            device=self.device_a, module=self.module, name='Outlet 1', power_port=power_port
        )
        self._assert_move_blocked('power outlet')

    def test_attached_inventory_item_blocks(self):
        InventoryItem.objects.create(device=self.device_a, name='Item 1', component=self.interface)
        self._assert_move_blocked('inventory items')

    def test_intra_module_bridge_pair_is_allowed(self):
        other = Interface.objects.create(
            device=self.device_a, module=self.module, name='eth1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        self.interface.bridge = other
        self.interface.save()
        self._assert_move_allowed()

    def test_intra_module_power_pair_is_allowed(self):
        power_port = PowerPort.objects.create(device=self.device_a, module=self.module, name='PP 1')
        PowerOutlet.objects.create(
            device=self.device_a, module=self.module, name='Outlet 1', power_port=power_port
        )
        self._assert_move_allowed()

    def test_mac_address_is_allowed(self):
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55', assigned_object=self.interface)
        self.interface.primary_mac_address = mac
        self.interface.save()
        self._assert_move_allowed()


class ModuleCrossDeviceMoveTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer M', slug='manufacturer-m')
        role = DeviceRole.objects.create(name='Role 1', slug='role-1')
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Chassis', slug='chassis')
        ModuleBayTemplate.objects.create(device_type=device_type, name='Slot 1', position='1')
        ModuleBayTemplate.objects.create(device_type=device_type, name='Slot 2', position='2')

        cls.line_card_type = ModuleType.objects.create(manufacturer=manufacturer, model='Line Card')
        InterfaceTemplate.objects.create(
            module_type=cls.line_card_type, name='Ethernet{module}/1', type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )
        power_port_template = PowerPortTemplate.objects.create(module_type=cls.line_card_type, name='PP 1')
        PowerOutletTemplate.objects.create(
            module_type=cls.line_card_type, name='Outlet 1', power_port=power_port_template
        )
        front_port_template = FrontPortTemplate.objects.create(
            module_type=cls.line_card_type, name='Front 1', type=PortTypeChoices.TYPE_LC
        )
        rear_port_template = RearPortTemplate.objects.create(
            module_type=cls.line_card_type, name='Rear 1', type=PortTypeChoices.TYPE_LC, positions=1
        )
        PortTemplateMapping.objects.create(
            module_type=cls.line_card_type,
            front_port=front_port_template, front_port_position=1,
            rear_port=rear_port_template, rear_port_position=1,
        )
        ModuleBayTemplate.objects.create(
            module_type=cls.line_card_type, name='SFP bay {module}/1', position='{module}/1'
        )
        cls.sfp_type = ModuleType.objects.create(manufacturer=manufacturer, model='SFP')
        InterfaceTemplate.objects.create(
            module_type=cls.sfp_type, name='SFP {module}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        cls.device_a = Device.objects.create(
            name='Chassis A', device_type=device_type, role=role, site=cls.site_a
        )
        cls.device_b = Device.objects.create(
            name='Chassis B', device_type=device_type, role=role, site=cls.site_b
        )
        cls.slot_1_a = cls.device_a.modulebays.get(name='Slot 1')
        cls.slot_2_b = cls.device_b.modulebays.get(name='Slot 2')
        cls.line_card = Module.objects.create(
            device=cls.device_a, module_bay=cls.slot_1_a, module_type=cls.line_card_type
        )
        cls.sfp_bay = cls.line_card.modulebays.get(name='SFP bay 1/1')
        cls.sfp_module = Module.objects.create(
            device=cls.device_a, module_bay=cls.sfp_bay, module_type=cls.sfp_type
        )

    def _move_to_device_b(self):
        self.line_card.device = self.device_b
        self.line_card.module_bay = self.slot_2_b
        self.line_card.full_clean()
        self.line_card.save()

    def test_cross_device_move_updates_subtree(self):
        sfp_interface = self.sfp_module.interfaces.get(name='SFP 1/1')
        previous = sfp_interface.last_updated
        self._move_to_device_b()

        self.line_card.refresh_from_db()
        self.assertEqual(self.line_card.device, self.device_b)
        self.assertEqual(self.line_card.module_bay, self.slot_2_b)

        self.sfp_module.refresh_from_db()
        self.assertEqual(self.sfp_module.device, self.device_b)

        self.sfp_bay.refresh_from_db()
        self.assertEqual(self.sfp_bay.device, self.device_b)
        self.assertEqual(self.sfp_bay._site, self.site_b)
        self.assertEqual(self.sfp_bay.parent_id, self.slot_2_b.pk)
        self.assertTrue(str(self.sfp_bay.path).startswith(f'{self.slot_2_b.path}.'))

        sfp_interface.refresh_from_db()
        self.assertEqual(sfp_interface.device, self.device_b)
        self.assertEqual(sfp_interface._site, self.site_b)
        self.assertGreater(sfp_interface.last_updated, previous)

    def test_cross_device_move_renames_templated_components(self):
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        sfp_interface = self.sfp_module.interfaces.get(name='SFP 1/1')
        self._move_to_device_b()
        interface.refresh_from_db()
        self.assertEqual(interface.name, 'Ethernet2/1')
        sfp_interface.refresh_from_db()
        self.assertEqual(sfp_interface.name, 'SFP 2/1')

    def test_cross_device_move_applies_swap_chain_bay_renames(self):
        """
        A rename chain where one bay's new name equals another moved bay's current name
        applies cleanly cross-device, with both bays renamed on the destination device.
        """
        # Templates resolve Bay E1/1 -> Bay E2/1 and Bay E2/1 -> Bay E2/2 across slots
        ModuleBayTemplate.objects.create(module_type=self.line_card_type, name='Bay E2/{module}')
        ModuleBayTemplate.objects.create(module_type=self.line_card_type, name='Bay E{module}/1')
        bay_1 = ModuleBay.objects.create(device=self.device_a, module=self.line_card, name='Bay E1/1')
        bay_2 = ModuleBay.objects.create(device=self.device_a, module=self.line_card, name='Bay E2/1')
        self._move_to_device_b()
        bay_1.refresh_from_db()
        bay_2.refresh_from_db()
        self.assertEqual(bay_1.name, 'Bay E2/1')
        self.assertEqual(bay_2.name, 'Bay E2/2')
        self.assertEqual(bay_1.device, self.device_b)
        self.assertEqual(bay_2.device, self.device_b)

    def test_cross_device_move_updates_port_mappings(self):
        mapping = PortMapping.objects.get(front_port__module=self.line_card)
        self._move_to_device_b()
        mapping.refresh_from_db()
        self.assertEqual(mapping.device, self.device_b)

    def test_cross_device_move_keeps_intra_module_power_link(self):
        outlet = self.line_card.poweroutlets.get(name='Outlet 1')
        self._move_to_device_b()
        outlet.refresh_from_db()
        self.assertEqual(outlet.device, self.device_b)
        self.assertEqual(outlet.power_port.device_id, self.device_b.pk)

    def test_cross_device_move_moves_mac_address(self):
        interface = self.line_card.interfaces.get(name='Ethernet1/1')
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55', assigned_object=interface)
        self._move_to_device_b()
        mac.refresh_from_db()
        interface.refresh_from_db()
        self.assertEqual(mac.assigned_object, interface)
        self.assertEqual(interface.device, self.device_b)

    def test_cross_device_move_recomputes_counters(self):
        self._move_to_device_b()
        self.device_a.refresh_from_db()
        self.device_b.refresh_from_db()
        self.assertEqual(self.device_a.interface_count, 0)
        self.assertEqual(self.device_b.interface_count, 2)
        self.assertEqual(self.device_a.module_bay_count, 2)
        self.assertEqual(self.device_b.module_bay_count, 3)

    def test_move_query_count_independent_of_destination_size(self):
        def move_and_count(destination_device, destination_bay):
            module = Module.objects.create(
                device=self.device_a, module_bay=self.device_a.modulebays.get(name='Slot 2'),
                module_type=self.sfp_type,
            )
            module.device = destination_device
            module.module_bay = destination_bay
            module.full_clean()
            with CaptureQueriesContext(connection) as ctx:
                module.save()
            return len(ctx.captured_queries)

        small_count = move_and_count(self.device_b, self.slot_2_b)
        big_device = Device.objects.create(
            name='Warehouse', device_type=self.device_b.device_type, role=self.device_b.role,
            site=self.site_b,
        )
        ModuleBay.objects.bulk_create([
            ModuleBay(device=big_device, name=f'Storage Bay {i}') for i in range(1, 201)
        ])
        target_bay = ModuleBay.objects.create(device=big_device, name='Target Bay')
        big_count = move_and_count(big_device, target_bay)
        self.assertEqual(small_count, big_count)

    def test_move_query_count_independent_of_same_type_child_count(self):
        """
        Moving a module with several installed children of the same module_type issues
        the same number of template-table queries as moving one with a single child: the
        per-pass template lookup is cached per module_type, not repeated per module.
        """
        multi_type = ModuleType.objects.create(
            manufacturer=self.line_card_type.manufacturer, model='Multi-Slot Card'
        )
        for i in range(1, 4):
            ModuleBayTemplate.objects.create(module_type=multi_type, name=f'Child Bay {i}', position=str(i))

        def build_and_move(child_count):
            device = create_test_device(f'Card Device {child_count}')
            card_bay = ModuleBay.objects.create(device=device, name='Card Bay')
            target_bay = ModuleBay.objects.create(device=device, name='Target Bay')
            card = Module.objects.create(device=device, module_bay=card_bay, module_type=multi_type)
            for child_bay in card.modulebays.order_by('name')[:child_count]:
                Module.objects.create(device=device, module_bay=child_bay, module_type=self.sfp_type)
            card.module_bay = target_bay
            card.full_clean()
            with CaptureQueriesContext(connection) as ctx:
                card.save()
            return sum(1 for query in ctx.captured_queries if 'template' in query['sql'].lower())

        one_child_queries = build_and_move(1)
        three_children_queries = build_and_move(3)
        self.assertEqual(one_child_queries, three_children_queries)

    def test_cross_device_move_refreshes_bay_sort_path(self):
        """
        The trigger-maintained sort_path of a moved nested bay reflects the
        destination hierarchy and the renamed chain after reparent plus rename.
        """
        old_sort_path = self.sfp_bay.sort_path
        self._move_to_device_b()
        moved_bay = ModuleBay.objects.get(pk=self.sfp_bay.pk)
        dest_bay = ModuleBay.objects.get(pk=self.slot_2_b.pk)
        self.assertEqual(moved_bay.name, 'SFP bay 2/1')
        self.assertTrue(str(moved_bay.path).startswith(f'{dest_bay.path}.'))
        self.assertNotEqual(moved_bay.sort_path, old_sort_path)
        self.assertTrue(str(moved_bay.sort_path).startswith(str(dest_bay.sort_path)))
        self.assertIn('SFP bay 2/1', str(moved_bay.sort_path))
