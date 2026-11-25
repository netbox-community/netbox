import uuid
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from core.signals import _signals_received
from dcim.models import (
    Cable,
    CableTermination,
    Device,
    Interface,
    MACAddress,
    Site,
    VirtualChassis,
)
from extras.models import Tag
from extras.validators import CustomValidator
from ipam.models import IPAddress
from netbox.context_managers import event_tracking
from users.models import User
from utilities.exceptions import AbortRequest
from utilities.fields import CounterCacheField
from utilities.serialization import deserialize_object, serialize_object
from utilities.testing.utils import create_test_device, create_test_virtualmachine
from virtualization.models import VirtualMachine, VMInterface

CREATE = ObjectChangeActionChoices.ACTION_CREATE
UPDATE = ObjectChangeActionChoices.ACTION_UPDATE
DELETE = ObjectChangeActionChoices.ACTION_DELETE

# Not compared: set by each save, or (CablePaths) rebuilt with new IDs
IGNORED_FIELDS = ('created', 'last_updated', '_path', '_config_context_generation')


class ChangeLogReplayTestCase(TestCase):
    """
    Check that the changes recorded for a request can be replayed in the order recorded, and reversed in the opposite
    order, one at a time: each must be valid given only the changes before it (or, in reverse, after it). Changes made
    as a side effect of saving or deleting another object are the ones at risk.

    The replay here is deliberately simple: an update sets the fields which changed, validates and saves; a deletion is
    reversed by validating and saving the recorded object.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')

    def setUp(self):
        _signals_received.pre_delete = set()

    #
    # Helpers
    #

    def _record(self, change):
        """Make a change under change logging and return the ObjectChanges recorded, in order."""
        last_pk = ObjectChange.objects.order_by('-pk').values_list('pk', flat=True).first() or 0
        request = RequestFactory().get(reverse('home'))
        request.id = uuid.uuid4()
        request.user = self.user
        with event_tracking(request):
            change()
        return list(ObjectChange.objects.filter(pk__gt=last_pk).order_by('pk'))

    @staticmethod
    def _state(models):
        state = {}
        for model in models:
            # Counter caches are recorded with each change, so replaying the changes to the objects counted as well
            # counts them twice (a separate problem from the order of the changes)
            counters = [field.name for field in model._meta.concrete_fields if isinstance(field, CounterCacheField)]
            for obj in model.objects.order_by('pk'):
                data = serialize_object(obj)
                for field in (*IGNORED_FIELDS, *counters):
                    data.pop(field, None)
                state[(model._meta.label, obj.pk)] = data
        return state

    def _assert_state(self, models, expected, msg):
        actual = self._state(models)
        differences = {}
        for key in actual.keys() | expected.keys():
            a, e = actual.get(key), expected.get(key)
            if a is None or e is None:
                differences[key] = 'unexpected' if e is None else 'missing'
            elif a != e:
                differences[key] = {field: (a.get(field), e.get(field)) for field in a if a.get(field) != e.get(field)}
        self.assertEqual(differences, {}, msg)

    @staticmethod
    def _insert(model, pk, data, raw):
        instance = deserialize_object(model, data, pk=pk)
        instance.object.full_clean()
        if raw:
            instance.save()
        else:
            instance.object.save(force_insert=True)
            for accessor, objects in (instance.m2m_data or {}).items():
                getattr(instance.object, accessor).set(objects)

    @staticmethod
    def _update(model, pk, source, target):
        obj = model.objects.get(pk=pk)
        m2m = {}
        for key in source.keys() | target.keys():
            if source.get(key) == (value := target.get(key)):
                continue
            if key == 'custom_fields':
                obj.custom_field_data = value
            elif key == 'tags':
                m2m[key] = Tag.objects.filter(name__in=value)
            elif key not in {field.name for field in model._meta.get_fields()}:
                # Not a field (e.g. a cable's terminations, which are recorded as changes of their own)
                continue
            elif (field := model._meta.get_field(key)).many_to_many:
                m2m[key] = value
            elif field.is_relation:
                setattr(obj, field.attname, value)
            else:
                setattr(obj, key, field.to_python(value))
        obj.full_clean()
        obj.save()
        for key, value in m2m.items():
            getattr(obj, key).set(value)

    def _apply(self, change, reverse=False):
        model = change.changed_object_type.model_class()
        pk = change.changed_object_id
        action = change.action
        if reverse and action != UPDATE:
            action = DELETE if action == CREATE else CREATE
        if action == CREATE:
            # A reversed deletion is saved normally, so that the model derives what the clean data leaves out
            self._insert(model, pk, change.prechange_data_clean if reverse else change.postchange_data, raw=not reverse)
        elif action == DELETE:
            model.objects.get(pk=pk).delete()
        elif reverse:
            self._update(model, pk, change.postchange_data_clean, change.prechange_data_clean)
        else:
            self._update(model, pk, change.prechange_data_clean, change.postchange_data_clean)

    def _replay(self, changes, reverse=False):
        for change in reversed(changes) if reverse else changes:
            try:
                self._apply(change, reverse=reverse)
            except Exception as e:
                position = changes.index(change) + 1
                verb = 'reversing' if reverse else 'replaying'
                e.add_note(f'While {verb} change {position} of {len(changes)}: {change}')
                raise

    def assertReplayable(self, change, models, expected):
        """
        Make a change, check the changes recorded for it against `expected`, a list of (action, model), then reverse,
        replay and reverse them again, checking the state of `models` each time.
        """
        original = self._state(models)
        changes = self._record(change)
        changed = self._state(models)
        self.assertNotEqual(changed, original)

        recorded = [(change.action, change.changed_object_type.model_class()) for change in changes]
        self.assertEqual(recorded, expected)

        self._replay(changes, reverse=True)
        self._assert_state(models, original, 'Unexpected state after reversing the changes')
        self._replay(changes)
        self._assert_state(models, changed, 'Unexpected state after replaying the changes')
        self._replay(changes, reverse=True)
        self._assert_state(models, original, 'Unexpected state after reversing the changes again')

        return changes

    @staticmethod
    def _create_cabled_interfaces():
        devices = [create_test_device(f'Device {i}') for i in (1, 2)]
        interfaces = [Interface.objects.create(device=device, name='eth0', type='1000base-t') for device in devices]
        cable = Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[1]])
        cable.save()
        return cable, interfaces

    #
    # References released ahead of a deletion
    #

    def test_cable_delete(self):
        cable, _ = self._create_cabled_interfaces()

        self.assertReplayable(
            lambda: Cable.objects.get(pk=cable.pk).delete(),
            (Cable, CableTermination, Interface),
            [
                (DELETE, CableTermination),
                (UPDATE, Interface),
                (DELETE, CableTermination),
                (UPDATE, Interface),
                (DELETE, Cable),
            ],
        )

    def test_cable_queryset_delete(self):
        cable, _ = self._create_cabled_interfaces()

        self.assertReplayable(
            lambda: Cable.objects.filter(pk=cable.pk).delete(),
            (Cable, CableTermination, Interface),
            [
                (DELETE, CableTermination),
                (UPDATE, Interface),
                (DELETE, CableTermination),
                (UPDATE, Interface),
                (DELETE, Cable),
            ],
        )

    def test_cable_create(self):
        devices = [create_test_device(f'Device {i}') for i in (1, 2)]
        interfaces = [Interface.objects.create(device=device, name='eth0', type='1000base-t') for device in devices]

        def change():
            Cable(
                a_terminations=[Interface.objects.get(pk=interfaces[0].pk)],
                b_terminations=[Interface.objects.get(pk=interfaces[1].pk)],
            ).save()

        self.assertReplayable(
            change,
            (Cable, CableTermination, Interface),
            [
                (CREATE, Cable),
                (CREATE, CableTermination),
                (UPDATE, Interface),
                (CREATE, CableTermination),
                (UPDATE, Interface),
                (UPDATE, Cable),
            ],
        )

    def test_nullable_reference_delete(self):
        """An object referring to a deleted object through a nullable foreign key is updated ahead of the deletion."""
        device = create_test_device('Device 1')
        lag = Interface.objects.create(device=device, name='ae0', type='lag')
        Interface.objects.create(device=device, name='eth0', type='1000base-t', lag=lag)

        self.assertReplayable(
            lambda: Interface.objects.get(pk=lag.pk).delete(),
            (Interface,),
            [(UPDATE, Interface), (DELETE, Interface)],
        )

    def test_tag_delete(self):
        """An object assigned a deleted tag is updated ahead of the deletion."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        tag = Tag.objects.create(name='Tag 1', slug='tag-1')
        site.tags.add(tag)

        self.assertReplayable(
            lambda: Tag.objects.get(pk=tag.pk).delete(),
            (Tag, Site),
            [(UPDATE, Site), (DELETE, Tag)],
        )

    def _create_device_ip(self, field_name):
        device = create_test_device('Device 1')
        interface = Interface.objects.create(device=device, name='eth0', type='1000base-t')
        ip = IPAddress.objects.create(address='192.0.2.1/24', assigned_object=interface)
        device.refresh_from_db()
        setattr(device, field_name, ip)
        device.save()
        return device, ip

    def test_primary_ip_delete(self):
        _, ip = self._create_device_ip('primary_ip4')

        self.assertReplayable(
            lambda: IPAddress.objects.get(pk=ip.pk).delete(),
            (IPAddress, Device),
            [(UPDATE, Device), (DELETE, IPAddress)],
        )

    def test_primary_ip_queryset_delete(self):
        """A queryset bypasses the model's deletion hook, so the reference is released after the deletion."""
        _, ip = self._create_device_ip('primary_ip4')

        changes = self._record(lambda: IPAddress.objects.filter(pk=ip.pk).delete())

        self.assertEqual(
            [(change.action, change.changed_object_type.model_class()) for change in changes],
            [(DELETE, IPAddress), (UPDATE, Device)],
        )

    def test_oob_ip_delete(self):
        _, ip = self._create_device_ip('oob_ip')

        self.assertReplayable(
            lambda: IPAddress.objects.get(pk=ip.pk).delete(),
            (IPAddress, Device),
            [(UPDATE, Device), (DELETE, IPAddress)],
        )

    def test_virtual_machine_primary_ip_delete(self):
        vm = create_test_virtualmachine('VM 1')
        interface = VMInterface.objects.create(virtual_machine=vm, name='eth0')
        ip = IPAddress.objects.create(address='2001:db8::1/64', assigned_object=interface)
        vm.primary_ip6 = ip
        vm.save()

        self.assertReplayable(
            lambda: IPAddress.objects.get(pk=ip.pk).delete(),
            (IPAddress, VirtualMachine),
            [(UPDATE, VirtualMachine), (DELETE, IPAddress)],
        )

    def test_device_with_primary_ip_delete(self):
        """A device deleted along with its primary IP address releases it first, as it is restored before it."""
        device, _ = self._create_device_ip('primary_ip4')

        self.assertReplayable(
            lambda: Device.objects.get(pk=device.pk).delete(),
            (IPAddress, Interface, Device),
            [(UPDATE, Device), (DELETE, IPAddress), (DELETE, Interface), (DELETE, Device)],
        )

    def _create_primary_mac(self):
        device = create_test_device('Device 1')
        interface = Interface.objects.create(device=device, name='eth0', type='1000base-t')
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55', assigned_object=interface)
        interface.primary_mac_address = mac
        interface.save()
        return interface, mac

    def test_primary_mac_delete(self):
        _, mac = self._create_primary_mac()

        self.assertReplayable(
            lambda: MACAddress.objects.get(pk=mac.pk).delete(),
            (MACAddress, Interface),
            [(UPDATE, Interface), (DELETE, MACAddress)],
        )

    def test_interface_with_primary_mac_delete(self):
        """An interface deleted along with its primary MAC address releases it first, as it is restored before it."""
        interface, _ = self._create_primary_mac()

        self.assertReplayable(
            lambda: Interface.objects.get(pk=interface.pk).delete(),
            (MACAddress, Interface),
            [(UPDATE, Interface), (DELETE, MACAddress), (DELETE, Interface)],
        )

    def _create_circuit(self):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuit = Circuit.objects.create(cid='Circuit 1', provider=provider, type=circuit_type)
        site = Site.objects.create(name='Site 1', slug='site-1')
        termination = CircuitTermination.objects.create(circuit=circuit, term_side='A', termination=site)
        return circuit, termination

    def test_circuit_termination_delete(self):
        _, termination = self._create_circuit()

        self.assertReplayable(
            lambda: CircuitTermination.objects.get(pk=termination.pk).delete(),
            (Circuit, CircuitTermination),
            [(UPDATE, Circuit), (DELETE, CircuitTermination)],
        )

    def test_circuit_delete(self):
        """A circuit deleted along with its terminations releases them first, as it is restored before them."""
        circuit, _ = self._create_circuit()

        self.assertReplayable(
            lambda: Circuit.objects.get(pk=circuit.pk).delete(),
            (Circuit, CircuitTermination),
            [(UPDATE, Circuit), (DELETE, CircuitTermination), (DELETE, Circuit)],
        )

    #
    # References between two objects, each made in a change of its own
    #

    def test_interface_create_with_primary_mac(self):
        device = create_test_device('Device 1')
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55')

        def change():
            Interface.objects.create(
                device=device, name='eth0', type='1000base-t', primary_mac_address=MACAddress.objects.get(pk=mac.pk)
            )

        changes = self.assertReplayable(
            change,
            (Interface, MACAddress),
            [(CREATE, Interface), (UPDATE, MACAddress), (UPDATE, Interface)],
        )
        self.assertIsNone(changes[0].postchange_data['primary_mac_address'])
        self.assertEqual(changes[2].postchange_data['primary_mac_address'], mac.pk)

    def test_vminterface_create_with_primary_mac(self):
        vm = create_test_virtualmachine('VM 1')
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55')

        def change():
            VMInterface.objects.create(
                virtual_machine=vm, name='eth0', primary_mac_address=MACAddress.objects.get(pk=mac.pk)
            )

        self.assertReplayable(
            change,
            (VMInterface, MACAddress),
            [(CREATE, VMInterface), (UPDATE, MACAddress), (UPDATE, VMInterface)],
        )

    def test_virtual_chassis_create_with_master(self):
        device = create_test_device('Device 1')

        changes = self.assertReplayable(
            lambda: VirtualChassis.objects.create(name='VC 1', master=Device.objects.get(pk=device.pk)),
            (VirtualChassis, Device),
            [(CREATE, VirtualChassis), (UPDATE, Device), (UPDATE, VirtualChassis)],
        )
        self.assertIsNone(changes[0].postchange_data['master'])
        self.assertEqual(changes[2].postchange_data['master'], device.pk)

    def test_virtual_chassis_delete(self):
        devices = [create_test_device(f'Device {i}') for i in (1, 2)]
        vc = VirtualChassis.objects.create(name='VC 1', master=devices[0])
        member = Device.objects.get(pk=devices[1].pk)
        member.virtual_chassis = vc
        member.vc_position = 2
        member.vc_priority = 10
        member.save()

        changes = self.assertReplayable(
            lambda: VirtualChassis.objects.get(pk=vc.pk).delete(),
            (VirtualChassis, Device),
            [(UPDATE, VirtualChassis), (UPDATE, Device), (UPDATE, Device), (DELETE, VirtualChassis)],
        )
        self.assertIsNone(changes[0].postchange_data['master'])
        self.assertIsNone(changes[3].prechange_data['master'])

    #
    # Protection rules and queryset deletions
    #

    def test_protection_rule_sees_object_before_references_are_released(self):
        device, _ = self._create_device_ip('primary_ip4')
        seen = []

        class Validator(CustomValidator):
            def validate(self, instance, request):
                seen.append(instance.primary_ip4_id)

        with override_settings(PROTECTION_RULES={'dcim.device': [Validator()]}):
            self._record(lambda: Device.objects.get(pk=device.pk).delete())

        self.assertEqual(seen, [device.primary_ip4_id])

    def test_primary_mac_queryset_delete(self):
        """A queryset bypasses the model's deletion hook, but the release of the primary MAC is still recorded."""
        interface, mac = self._create_primary_mac()

        changes = self._record(lambda: MACAddress.objects.filter(pk=mac.pk).delete())

        self.assertEqual(
            [(change.action, change.changed_object_type.model_class()) for change in changes],
            [(DELETE, MACAddress), (UPDATE, Interface)],
        )
        interface.refresh_from_db()
        self.assertIsNone(interface.primary_mac_address)

    def test_interface_create_with_primary_mac_is_atomic(self):
        device = create_test_device('Device 1')
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55')
        interface = Interface(device=device, name='eth0', type='1000base-t', primary_mac_address=mac)

        with patch.object(MACAddress, 'save', side_effect=RuntimeError), self.assertRaises(RuntimeError):
            interface.save()

        self.assertFalse(Interface.objects.filter(device=device).exists())
        self.assertEqual(interface.primary_mac_address, mac)
        self.assertIsNone(interface.pk)

        # The interface can be saved again as if for the first time
        interface.save()
        mac.refresh_from_db()
        self.assertEqual(mac.assigned_object, interface)

    def test_protection_rule_sees_object_while_still_referenced(self):
        _, ip = self._create_device_ip('primary_ip4')
        rules = {'ipam.ipaddress': [{'is_primary_ip': {'eq': False}}]}

        with override_settings(PROTECTION_RULES=rules), self.assertRaises(AbortRequest):
            self._record(lambda: IPAddress.objects.get(pk=ip.pk).delete())

    def test_interface_queryset_delete_records_nothing_after_the_deletion(self):
        """An interface deleted through a queryset along with its primary MAC is not updated after its deletion."""
        interface, _ = self._create_primary_mac()

        changes = self._record(lambda: Interface.objects.filter(pk=interface.pk).delete())

        interface_changes = [change.action for change in changes if change.changed_object_type.model == 'interface']
        self.assertEqual(interface_changes[-1], DELETE)
        self.assertEqual(interface_changes.count(DELETE), 1)
        self.assertNotIn(UPDATE, interface_changes)
