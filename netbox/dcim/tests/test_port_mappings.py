import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase, tag
from django.urls import reverse
from rest_framework import status

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from dcim.choices import PortTypeChoices
from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    FrontPort,
    FrontPortTemplate,
    Manufacturer,
    PortMapping,
    PortTemplateMapping,
    RearPort,
    RearPortTemplate,
    Site,
)
from dcim.utils import reconcile_port_mappings
from netbox.context_managers import event_tracking
from users.models import User
from utilities.testing import APITestCase


def _build_request(user):
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = user
    return request


class ReconcilePortMappingsTestCase(TestCase):
    """
    Exercise dcim.utils.reconcile_port_mappings and confirm that PortMapping now participates in
    change logging (#22644): only the difference is written, so unchanged mappings keep their PK and
    emit no ObjectChange.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pw')

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')
        site = Site.objects.create(name='Site 1', slug='site-1')
        cls.device = Device.objects.create(device_type=device_type, role=role, name='Device 1', site=site)

        cls.front_port = FrontPort.objects.create(
            device=cls.device, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, positions=4
        )
        cls.rear_ports = [
            RearPort.objects.create(
                device=cls.device, name=f'Rear Port {i}', type=PortTypeChoices.TYPE_8P8C, positions=4
            )
            for i in range(1, 4)
        ]

    def _desired(self, *pairs):
        # Each pair is (front_port_position, rear_port, rear_port_position).
        return [
            {'front_port_position': fpp, 'rear_port_id': rp.pk, 'rear_port_position': rpp}
            for fpp, rp, rpp in pairs
        ]

    def _reconcile(self, desired):
        request = _build_request(self.user)
        with event_tracking(request):
            reconcile_port_mappings(PortMapping, parent_field='front_port', parent=self.front_port, desired=desired)

    def _mapping_changes(self, action=None):
        changes = ObjectChange.objects.filter(changed_object_type=ContentType.objects.get_for_model(PortMapping))
        if action is not None:
            changes = changes.filter(action=action)
        return changes

    def _current_pks(self):
        return set(PortMapping.objects.filter(front_port=self.front_port).values_list('pk', flat=True))

    def test_create_records_objectchange(self):
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[1], 1),
        ))

        self.assertEqual(PortMapping.objects.filter(front_port=self.front_port).count(), 2)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_CREATE).count(), 2)

    @tag('regression')  # Ref: #22644
    def test_noop_resave_writes_nothing(self):
        # Re-saving a front port without changing its wiring must not mint new PKs or emit changelog
        # entries — this is what previously broke branch merges (colliding on the unique constraint
        # when both sides replayed DELETE(old-pk) + CREATE(new-pk)).
        desired = self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[1], 1),
        )
        self._reconcile(desired)
        original_pks = self._current_pks()
        ObjectChange.objects.all().delete()

        self._reconcile(desired)

        self.assertEqual(self._mapping_changes().count(), 0)
        self.assertEqual(self._current_pks(), original_pks)

    def test_repointing_a_slot_deletes_and_creates(self):
        self._reconcile(self._desired((1, self.rear_ports[0], 1)))
        original_pk = self._current_pks().pop()
        ObjectChange.objects.all().delete()

        # Same front port position, different rear port: the slot is re-pointed.
        self._reconcile(self._desired((1, self.rear_ports[1], 1)))

        mappings = PortMapping.objects.filter(front_port=self.front_port)
        self.assertEqual(mappings.count(), 1)
        mapping = mappings.first()
        self.assertEqual(mapping.rear_port_id, self.rear_ports[1].pk)
        self.assertNotEqual(mapping.pk, original_pk)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_DELETE).count(), 1)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_CREATE).count(), 1)

    def test_unchanged_rows_survive_alongside_changed_rows(self):
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[1], 1),
        ))
        unchanged_pk = PortMapping.objects.get(front_port=self.front_port, front_port_position=1).pk
        ObjectChange.objects.all().delete()

        # Position 1 is untouched; position 2 is re-pointed to a third rear port.
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[2], 1),
        ))

        self.assertEqual(PortMapping.objects.get(front_port=self.front_port, front_port_position=1).pk, unchanged_pk)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_CREATE).count(), 1)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_DELETE).count(), 1)

    def test_removing_a_mapping_records_delete(self):
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[1], 1),
        ))
        ObjectChange.objects.all().delete()

        self._reconcile(self._desired((1, self.rear_ports[0], 1)))

        self.assertEqual(PortMapping.objects.filter(front_port=self.front_port).count(), 1)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_DELETE).count(), 1)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_CREATE).count(), 0)

    def test_swapping_positions_preserves_constraints(self):
        # Two front port positions pointing at the same rear port's positions 1 and 2.
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 1),
            (2, self.rear_ports[0], 2),
        ))

        # Swap their rear port positions. Reconcile deletes both changed rows before recreating, so
        # the transient state never violates the (rear_port, rear_port_position) unique constraint.
        self._reconcile(self._desired(
            (1, self.rear_ports[0], 2),
            (2, self.rear_ports[0], 1),
        ))

        self.assertEqual(
            PortMapping.objects.get(front_port=self.front_port, front_port_position=1).rear_port_position, 2
        )
        self.assertEqual(
            PortMapping.objects.get(front_port=self.front_port, front_port_position=2).rear_port_position, 1
        )

    def test_direct_delete_records_objectchange(self):
        self._reconcile(self._desired((1, self.rear_ports[0], 1)))
        mapping = PortMapping.objects.get(front_port=self.front_port)
        mapping_pk = mapping.pk
        ObjectChange.objects.all().delete()

        request = _build_request(self.user)
        with event_tracking(request):
            mapping.delete()

        self.assertTrue(
            self._mapping_changes(ObjectChangeActionChoices.ACTION_DELETE).filter(changed_object_id=mapping_pk).exists()
        )


class ReconcilePortTemplateMappingsTestCase(TestCase):
    """
    Confirm reconcile_port_mappings and change logging behave identically for PortTemplateMapping.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pw')

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        cls.front_port = FrontPortTemplate.objects.create(
            device_type=cls.device_type, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, positions=4
        )
        cls.rear_ports = [
            RearPortTemplate.objects.create(
                device_type=cls.device_type, name=f'Rear Port {i}', type=PortTypeChoices.TYPE_8P8C, positions=4
            )
            for i in range(1, 3)
        ]

    def _desired(self, *pairs):
        return [
            {'front_port_position': fpp, 'rear_port_id': rp.pk, 'rear_port_position': rpp}
            for fpp, rp, rpp in pairs
        ]

    def _reconcile(self, desired):
        request = _build_request(self.user)
        with event_tracking(request):
            reconcile_port_mappings(
                PortTemplateMapping,
                parent_field='front_port',
                parent=self.front_port,
                desired=desired,
            )

    def _mapping_changes(self, action=None):
        changes = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(PortTemplateMapping)
        )
        if action is not None:
            changes = changes.filter(action=action)
        return changes

    def test_create_records_objectchange(self):
        self._reconcile(self._desired((1, self.rear_ports[0], 1)))

        mapping = PortTemplateMapping.objects.get(front_port=self.front_port)
        self.assertEqual(mapping.device_type_id, self.device_type.pk)
        self.assertEqual(self._mapping_changes(ObjectChangeActionChoices.ACTION_CREATE).count(), 1)

    @tag('regression')  # Ref: #22644
    def test_noop_resave_writes_nothing(self):
        desired = self._desired((1, self.rear_ports[0], 1))
        self._reconcile(desired)
        original_pk = PortTemplateMapping.objects.get(front_port=self.front_port).pk
        ObjectChange.objects.all().delete()

        self._reconcile(desired)

        self.assertEqual(self._mapping_changes().count(), 0)
        self.assertEqual(PortTemplateMapping.objects.get(front_port=self.front_port).pk, original_pk)


class PortMappingAPITestCase(APITestCase):
    """
    Exercise the reconcile behaviour through PortSerializer.create()/update() over the REST API,
    covering the model-instance -> _id normalization in PortSerializer._reconcile_mappings.
    """
    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')
        site = Site.objects.create(name='Site 1', slug='site-1')
        cls.device = Device.objects.create(device_type=device_type, role=role, name='Device 1', site=site)

        cls.rear_ports = [
            RearPort.objects.create(
                device=cls.device, name=f'Rear Port {i}', type=PortTypeChoices.TYPE_8P8C, positions=4
            )
            for i in range(1, 4)
        ]

        # An existing front port with two mappings, for the update/PATCH tests.
        cls.front_port = FrontPort.objects.create(
            device=cls.device, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, positions=2
        )
        PortMapping.objects.bulk_create([
            PortMapping(
                device=cls.device, front_port=cls.front_port, front_port_position=1,
                rear_port=cls.rear_ports[0], rear_port_position=1,
            ),
            PortMapping(
                device=cls.device, front_port=cls.front_port, front_port_position=2,
                rear_port=cls.rear_ports[1], rear_port_position=1,
            ),
        ])

    def _mapping_pks(self, front_port):
        return set(PortMapping.objects.filter(front_port=front_port).values_list('pk', flat=True))

    def _mapping_creates(self):
        return ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(PortMapping),
            action=ObjectChangeActionChoices.ACTION_CREATE,
        )

    def test_create_records_mappings_and_changelog(self):
        # Confirms PortSerializer.create() + _reconcile_mappings normalization (rear_port instance ->
        # rear_port_id) writes the mappings and records their ObjectChanges.
        self.add_permissions('dcim.add_frontport', 'dcim.view_frontport', 'dcim.view_rearport', 'dcim.view_device')
        data = {
            'device': self.device.pk,
            'name': 'Front Port 2',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 2,
            'rear_ports': [
                {'position': 1, 'rear_port': self.rear_ports[2].pk, 'rear_port_position': 1},
                {'position': 2, 'rear_port': self.rear_ports[2].pk, 'rear_port_position': 2},
            ],
        }
        response = self.client.post(reverse('dcim-api:frontport-list'), data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        front_port = FrontPort.objects.get(pk=response.data['id'])
        mappings = PortMapping.objects.filter(front_port=front_port).order_by('front_port_position')
        self.assertEqual(mappings.count(), 2)
        self.assertEqual(mappings[0].rear_port_id, self.rear_ports[2].pk)
        self.assertEqual(mappings[1].rear_port_position, 2)
        self.assertEqual(
            self._mapping_creates().filter(changed_object_id__in=mappings.values_list('pk', flat=True)).count(), 2
        )

    def test_update_omitting_rear_ports_preserves_mappings(self):
        # A PATCH that omits rear_ports must leave the existing mappings untouched.
        self.add_permissions('dcim.change_frontport', 'dcim.view_frontport')
        url = reverse('dcim-api:frontport-detail', kwargs={'pk': self.front_port.pk})
        original_pks = self._mapping_pks(self.front_port)

        response = self.client.patch(url, {'description': 'Updated'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self._mapping_pks(self.front_port), original_pks)

    def test_update_rewires_mappings(self):
        # Re-point both slots to new rear port pairs; reconcile deletes the old rows and creates the
        # replacements.
        self.add_permissions('dcim.change_frontport', 'dcim.view_frontport', 'dcim.view_rearport', 'dcim.view_device')
        url = reverse('dcim-api:frontport-detail', kwargs={'pk': self.front_port.pk})
        original_pks = self._mapping_pks(self.front_port)

        data = {
            'rear_ports': [
                {'position': 1, 'rear_port': self.rear_ports[2].pk, 'rear_port_position': 3},
                {'position': 2, 'rear_port': self.rear_ports[2].pk, 'rear_port_position': 4},
            ],
        }
        response = self.client.patch(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        mappings = PortMapping.objects.filter(front_port=self.front_port).order_by('front_port_position')
        self.assertEqual([m.rear_port_id for m in mappings], [self.rear_ports[2].pk, self.rear_ports[2].pk])
        self.assertEqual([m.rear_port_position for m in mappings], [3, 4])
        self.assertTrue(self._mapping_pks(self.front_port).isdisjoint(original_pks))
