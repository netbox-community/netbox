import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from ipam.models import IPAddress, Prefix
from netbox.context_managers import event_tracking
from users.models import User
from utilities.testing.utils import create_test_device, create_test_virtualmachine


def _build_request(user):
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = user
    return request


class PrefixHierarchySignalTestCase(TestCase):
    """
    Verify ipam.signals.handle_prefix_saved / handle_prefix_deleted keep the cached
    `_children` and `_depth` counters up to date as prefixes are added, modified, and
    removed.
    """

    def _refresh_counters(self, *prefixes):
        for prefix in prefixes:
            prefix.refresh_from_db()
        return prefixes

    def test_creating_prefix_initializes_hierarchy_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent, child)
        self.assertEqual(parent._children, 1)
        self.assertEqual(child._depth, 1)
        self.assertEqual(child._children, 0)

    def test_modifying_prefix_recomputes_old_and_new_position(self):
        parent_a = Prefix.objects.create(prefix='10.0.0.0/16')
        parent_b = Prefix.objects.create(prefix='192.168.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent_a, parent_b, child)
        self.assertEqual(parent_a._children, 1)
        self.assertEqual(parent_b._children, 0)

        # Move the child under parent_b.
        child.prefix = '192.168.1.0/24'
        child.save()

        self._refresh_counters(parent_a, parent_b, child)
        self.assertEqual(parent_a._children, 0)
        self.assertEqual(parent_b._children, 1)
        self.assertEqual(child._depth, 1)

    def test_unchanged_save_does_not_disturb_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent, child)
        original_children = parent._children
        original_depth = child._depth

        # Save with no field changes.
        parent.description = ''
        parent.save()

        self._refresh_counters(parent, child)
        self.assertEqual(parent._children, original_children)
        self.assertEqual(child._depth, original_depth)

    def test_deleting_prefix_recomputes_neighbor_counters(self):
        parent = Prefix.objects.create(prefix='10.0.0.0/16')
        child = Prefix.objects.create(prefix='10.0.1.0/24')

        self._refresh_counters(parent)
        self.assertEqual(parent._children, 1)

        child.delete()

        self._refresh_counters(parent)
        self.assertEqual(parent._children, 0)


class ClearPrimaryIPSignalTestCase(TestCase):
    """
    Verify ipam.signals.clear_primary_ip detaches deleted IPAddresses from the Device or
    VirtualMachine they were assigned as primary. The behavior under test is the
    signal-driven snapshot+save (and resulting change-log entry), not the FK's
    on_delete=SET_NULL fallback.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_device_primary_ip4_delete_records_device_update(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='192.0.2.1/24')
        device.primary_ip4 = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.primary_ip4)

        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip4'])

    def test_device_primary_ip6_delete_clears_field_and_saves(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='2001:db8::1/64')
        device.primary_ip6 = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.primary_ip6)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip6'])

    def test_vm_primary_ip4_delete_records_vm_update(self):
        vm = create_test_virtualmachine('VM 1')
        ip = IPAddress.objects.create(address='192.0.2.10/24')
        vm.primary_ip4 = ip
        vm.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        vm.refresh_from_db()
        self.assertIsNone(vm.primary_ip4)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(vm),
            changed_object_id=vm.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['primary_ip4'])

    def test_unrelated_ip_delete_records_no_device_change(self):
        device = create_test_device('Device 1')
        device_type = ContentType.objects.get_for_model(device)
        assigned = IPAddress.objects.create(address='192.0.2.1/24')
        unrelated = IPAddress.objects.create(address='192.0.2.2/24')
        device.primary_ip4 = assigned
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            unrelated.delete()

        device.refresh_from_db()
        self.assertEqual(device.primary_ip4, assigned)
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=device_type,
                changed_object_id=device.pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
            ).exists()
        )


class ClearOOBIPSignalTestCase(TestCase):
    """
    Verify ipam.signals.clear_oob_ip detaches a deleted IPAddress from any Device on
    which it was set as the OOB IP, and records a Device update change-log entry.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='pw')

    def test_device_oob_ip_delete_records_device_update(self):
        device = create_test_device('Device 1')
        ip = IPAddress.objects.create(address='192.0.2.1/24')
        device.oob_ip = ip
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            ip.delete()

        device.refresh_from_db()
        self.assertIsNone(device.oob_ip)
        oc = ObjectChange.objects.get(
            changed_object_type=ContentType.objects.get_for_model(device),
            changed_object_id=device.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        )
        self.assertIsNone(oc.postchange_data['oob_ip'])

    def test_unrelated_ip_delete_records_no_device_change(self):
        device = create_test_device('Device 1')
        device_type = ContentType.objects.get_for_model(device)
        oob = IPAddress.objects.create(address='192.0.2.1/24')
        unrelated = IPAddress.objects.create(address='192.0.2.2/24')
        device.oob_ip = oob
        device.save()

        request = _build_request(self.user)
        with event_tracking(request):
            unrelated.delete()

        device.refresh_from_db()
        self.assertEqual(device.oob_ip, oob)
        self.assertFalse(
            ObjectChange.objects.filter(
                changed_object_type=device_type,
                changed_object_id=device.pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
            ).exists()
        )
