from django.test import TestCase

from dcim.choices import (
    DeviceFaceChoices,
    DeviceStatusChoices,
    InterfaceModeChoices,
    InterfaceTypeChoices,
    PortTypeChoices,
)
from dcim.forms import *
from dcim.models import *
from ipam.models import VLAN
from utilities.testing import create_test_device
from virtualization.models import Cluster, ClusterGroup, ClusterType


def get_id(model, slug):
    return model.objects.get(slug=slug).id


class DeviceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        rack = Rack.objects.create(name='Rack 1', site=site)
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1', u_height=1
        )
        role = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )
        Platform.objects.create(name='Platform 1', slug='platform-1')
        Device.objects.create(
            name='Device 1', device_type=device_type, role=role, site=site, rack=rack, position=1
        )
        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster_group = ClusterGroup.objects.create(name='Cluster Group 1', slug='cluster-group-1')
        Cluster.objects.create(name='Cluster 1', type=cluster_type, group=cluster_group)

    def test_racked_device(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': Rack.objects.first().pk,
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 2,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_racked_device_occupied(self):
        form = DeviceForm(data={
            'name': 'test',
            'role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': Rack.objects.first().pk,
            'face': DeviceFaceChoices.FACE_FRONT,
            'position': 1,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('position', form.errors)

    def test_non_racked_device(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': None,
            'face': None,
            'position': None,
            'platform': Platform.objects.first().pk,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_non_racked_device_with_face(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': None,
            'face': DeviceFaceChoices.FACE_REAR,
            'platform': None,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('face', form.errors)

    def test_non_racked_device_with_position(self):
        form = DeviceForm(data={
            'name': 'New Device',
            'role': DeviceRole.objects.first().pk,
            'tenant': None,
            'manufacturer': Manufacturer.objects.first().pk,
            'device_type': DeviceType.objects.first().pk,
            'site': Site.objects.first().pk,
            'rack': None,
            'position': 10,
            'platform': None,
            'status': DeviceStatusChoices.STATUS_ACTIVE,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('position', form.errors)


class FrontPortTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Panel Device 1')
        cls.rear_ports = (
            RearPort(name='RearPort1', device=cls.device, type=PortTypeChoices.TYPE_8P8C),
            RearPort(name='RearPort2', device=cls.device, type=PortTypeChoices.TYPE_8P8C),
            RearPort(name='RearPort3', device=cls.device, type=PortTypeChoices.TYPE_8P8C),
            RearPort(name='RearPort4', device=cls.device, type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(cls.rear_ports)

    def test_front_port_label_count_valid(self):
        """
        Test that generating an equal number of names and labels passes form validation.
        """
        front_port_data = {
            'device': self.device.pk,
            'name': 'FrontPort[1-4]',
            'label': 'Port[1-4]',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port': [f'{rear_port.pk}:1' for rear_port in self.rear_ports],
        }
        form = FrontPortCreateForm(front_port_data)

        self.assertTrue(form.is_valid())

    def test_front_port_label_count_mismatch(self):
        """
        Check that attempting to generate a differing number of names and labels results in a validation error.
        """
        bad_front_port_data = {
            'device': self.device.pk,
            'name': 'FrontPort[1-4]',
            'label': 'Port[1-2]',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port': [f'{rear_port.pk}:1' for rear_port in self.rear_ports],
        }
        form = FrontPortCreateForm(bad_front_port_data)

        self.assertFalse(form.is_valid())
        self.assertIn('label', form.errors)


class InterfaceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')
        cls.vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
        )
        VLAN.objects.bulk_create(cls.vlans)
        cls.interface = Interface.objects.create(
            device=cls.device,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_GBIC,
            mode=InterfaceModeChoices.MODE_TAGGED,
        )

    def test_interface_label_count_valid(self):
        """
        Test that generating an equal number of names and labels passes form validation.
        """
        interface_data = {
            'device': self.device.pk,
            'name': 'eth[0-9]',
            'label': 'Interface[0-9]',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
        }
        form = InterfaceCreateForm(interface_data)

        self.assertTrue(form.is_valid())

    def test_interface_label_count_mismatch(self):
        """
        Check that attempting to generate a differing number of names and labels results in a validation error.
        """
        bad_interface_data = {
            'device': self.device.pk,
            'name': 'eth[0-9]',
            'label': 'Interface[0-1]',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
        }
        form = InterfaceCreateForm(bad_interface_data)

        self.assertFalse(form.is_valid())
        self.assertIn('label', form.errors)

    def test_create_interface_mode_valid_data(self):
        """
        Test that saving valid interface mode and tagged/untagged vlans works properly
        """

        # Validate access mode
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/1',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_ACCESS,
            'untagged_vlan': self.vlans[0].pk
        }
        form = InterfaceCreateForm(data)

        self.assertTrue(form.is_valid())

        # Validate tagged vlans
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/2',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': self.vlans[0].pk,
            'tagged_vlans': [self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceCreateForm(data)
        self.assertTrue(form.is_valid())

        # Validate tagged vlans
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/3',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_TAGGED_ALL,
            'untagged_vlan': self.vlans[0].pk,
        }
        form = InterfaceCreateForm(data)
        self.assertTrue(form.is_valid())

    def test_create_interface_mode_access_invalid_data(self):
        """
        Test that saving invalid interface mode and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/4',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_ACCESS,
            'untagged_vlan': self.vlans[0].pk,
            'tagged_vlans': [self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceCreateForm(data)

        self.assertTrue(form.is_valid())
        self.assertIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())

    def test_edit_interface_mode_access_invalid_data(self):
        """
        Test that saving invalid interface mode and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'Ethernet 1/5',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_ACCESS,
            'tagged_vlans': [self.vlans[0].pk, self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceForm(data, instance=self.interface)

        self.assertTrue(form.is_valid())
        self.assertIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())

    def test_create_interface_mode_tagged_all_invalid_data(self):
        """
        Test that saving invalid interface mode and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/6',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_TAGGED_ALL,
            'tagged_vlans': [self.vlans[0].pk, self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceCreateForm(data)

        self.assertTrue(form.is_valid())
        self.assertIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())

    def test_edit_interface_mode_tagged_all_invalid_data(self):
        """
        Test that saving invalid interface mode and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'Ethernet 1/7',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': InterfaceModeChoices.MODE_TAGGED_ALL,
            'tagged_vlans': [self.vlans[0].pk, self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceForm(data)
        self.assertTrue(form.is_valid())
        self.assertIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())

    def test_create_interface_mode_routed_invalid_data(self):
        """
        Test that saving invalid interface mode (routed) and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'ethernet1/6',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': None,
            'untagged_vlan': self.vlans[0].pk,
            'tagged_vlans': [self.vlans[0].pk, self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceCreateForm(data)

        self.assertTrue(form.is_valid())
        self.assertNotIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())

    def test_edit_interface_mode_routed_invalid_data(self):
        """
        Test that saving invalid interface mode (routed) and tagged/untagged vlans works properly
        """
        data = {
            'device': self.device.pk,
            'name': 'Ethernet 1/7',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mode': None,
            'untagged_vlan': self.vlans[0].pk,
            'tagged_vlans': [self.vlans[0].pk, self.vlans[1].pk, self.vlans[2].pk]
        }
        form = InterfaceForm(data)
        self.assertTrue(form.is_valid())
        self.assertNotIn('untagged_vlan', form.cleaned_data.keys())
        self.assertNotIn('tagged_vlans', form.cleaned_data.keys())
        self.assertNotIn('qinq_svlan', form.cleaned_data.keys())
