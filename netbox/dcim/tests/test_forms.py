from django.test import TestCase

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from dcim.choices import (
    CableTypeChoices, DeviceFaceChoices, DeviceStatusChoices, InterfaceModeChoices, InterfaceTypeChoices,
    PortTypeChoices, PowerOutletStatusChoices,
)
from dcim.forms import *
from dcim.models import *
from ipam.models import VLAN
from utilities.testing import create_test_device
from virtualization.models import Cluster, ClusterGroup, ClusterType


def get_id(model, slug):
    return model.objects.get(slug=slug).id


class PowerOutletFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = site = Site.objects.create(name='Site 1', slug='site-1')
        cls.manufacturer = manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.role = role = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )
        cls.device_type = device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1', u_height=1
        )
        cls.rack = rack = Rack.objects.create(name='Rack 1', site=site)
        cls.device = Device.objects.create(
            name='Device 1', device_type=device_type, role=role, site=site, rack=rack, position=1
        )

    def test_status_is_required(self):
        form = PowerOutletForm(data={
            'device': self.device,
            'module': None,
            'name': 'New Enabled Outlet',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_status_must_be_defined_choice(self):
        form = PowerOutletForm(data={
            'device': self.device,
            'module': None,
            'name': 'New Enabled Outlet',
            'status': 'this isn\'t a defined choice',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
        self.assertTrue(form.errors['status'][-1].startswith('Select a valid choice.'))

    def test_status_recognizes_choices(self):
        for index, choice in enumerate(PowerOutletStatusChoices.CHOICES):
            form = PowerOutletForm(data={
                'device': self.device,
                'module': None,
                'name': f'New Enabled Outlet {index + 1}',
                'status': choice[0],
            })
            self.assertEqual({}, form.errors)
            self.assertTrue(form.is_valid())
            instance = form.save()
            self.assertEqual(instance.status, choice[0])


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


class CableImportFormTestCase(TestCase):
    """
    Test cases for CableImportForm error handling and edge cases.

    Note: Happy path scenarios (successful cable creation) are covered by
    dcim.tests.test_views.CableTestCase which tests the bulk import view.
    These tests focus on validation errors and edge cases not covered by the view tests.
    """

    @classmethod
    def setUpTestData(cls):
        # Create sites
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')

        # Create manufacturer and device type
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device Type 1',
            slug='device-type-1',
        )
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')

        # Create devices
        cls.device_a1 = Device.objects.create(
            name='Device-A1',
            device_type=device_type,
            role=role,
            site=cls.site_a,
        )
        cls.device_a2 = Device.objects.create(
            name='Device-A2',
            device_type=device_type,
            role=role,
            site=cls.site_a,
        )
        # Device with same name in different site
        cls.device_b_duplicate = Device.objects.create(
            name='Device-A1',  # Same name as device_a1
            device_type=device_type,
            role=role,
            site=cls.site_b,
        )

        # Create interfaces
        cls.interface_a1_eth0 = Interface.objects.create(
            device=cls.device_a1,
            name='eth0',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )
        cls.interface_a2_eth0 = Interface.objects.create(
            device=cls.device_a2,
            name='eth0',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
        )

        # Create circuit for testing circuit not found error
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        cls.circuit = Circuit.objects.create(
            provider=provider,
            type=circuit_type,
            cid='CIRCUIT-001',
        )
        cls.circuit_term_a = CircuitTermination.objects.create(
            circuit=cls.circuit,
            term_side='A',
        )

        # Create provider network for testing provider network validation
        cls.provider_network = ProviderNetwork.objects.create(
            provider=provider,
            name='Provider Network 1',
        )

    def test_device_not_found(self):
        """Test error when parent device is not found."""
        form = CableImportForm(data={
            'side_a_site': 'Site A',
            'side_a_parent': 'NonexistentDevice',
            'side_a_type': 'dcim.interface',
            'side_a_name': 'eth0',
            'side_b_site': 'Site A',
            'side_b_parent': 'Device-A2',
            'side_b_type': 'dcim.interface',
            'side_b_name': 'eth0',
            'type': CableTypeChoices.TYPE_CAT6,
            'status': 'connected',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Side A: Device not found: NonexistentDevice', str(form.errors))

    def test_circuit_not_found(self):
        """Test error when circuit is not found."""
        form = CableImportForm(data={
            'side_a_site': None,
            'side_a_parent': 'NONEXISTENT-CID',
            'side_a_type': 'circuits.circuittermination',
            'side_a_name': 'A',
            'side_b_site': 'Site A',
            'side_b_parent': 'Device-A1',
            'side_b_type': 'dcim.interface',
            'side_b_name': 'eth0',
            'type': CableTypeChoices.TYPE_MMF_OM4,
            'status': 'connected',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Side A: Circuit not found: NONEXISTENT-CID', str(form.errors))

    def test_termination_not_found(self):
        """Test error when termination is not found on parent."""
        form = CableImportForm(data={
            'side_a_site': 'Site A',
            'side_a_parent': 'Device-A1',
            'side_a_type': 'dcim.interface',
            'side_a_name': 'eth999',  # Nonexistent interface
            'side_b_site': 'Site A',
            'side_b_parent': 'Device-A2',
            'side_b_type': 'dcim.interface',
            'side_b_name': 'eth0',
            'type': CableTypeChoices.TYPE_CAT6,
            'status': 'connected',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Side A: Interface not found', str(form.errors))

    def test_termination_already_cabled(self):
        """Test error when termination is already connected to a cable."""
        # Create an existing cable
        existing_cable = Cable.objects.create(type=CableTypeChoices.TYPE_CAT6, status='connected')
        self.interface_a1_eth0.cable = existing_cable
        self.interface_a1_eth0.save()

        form = CableImportForm(data={
            'side_a_site': 'Site A',
            'side_a_parent': 'Device-A1',
            'side_a_type': 'dcim.interface',
            'side_a_name': 'eth0',
            'side_b_site': 'Site A',
            'side_b_parent': 'Device-A2',
            'side_b_type': 'dcim.interface',
            'side_b_name': 'eth0',
            'type': CableTypeChoices.TYPE_CAT6,
            'status': 'connected',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('already connected', str(form.errors))

    def test_circuit_termination_with_provider_network(self):
        """Test error when circuit termination is already connected to a provider network."""
        from django.contrib.contenttypes.models import ContentType

        # Connect circuit termination to provider network
        circuit_term = CircuitTermination.objects.get(pk=self.circuit_term_a.pk)
        pn_ct = ContentType.objects.get_for_model(ProviderNetwork)
        circuit_term.termination_type = pn_ct
        circuit_term.termination_id = self.provider_network.pk
        circuit_term.save()

        try:
            form = CableImportForm(data={
                'side_a_site': None,
                'side_a_parent': 'CIRCUIT-001',
                'side_a_type': 'circuits.circuittermination',
                'side_a_name': 'A',
                'side_b_site': 'Site A',
                'side_b_parent': 'Device-A1',
                'side_b_type': 'dcim.interface',
                'side_b_name': 'eth0',
                'type': CableTypeChoices.TYPE_MMF_OM4,
                'status': 'connected',
            })
            self.assertFalse(form.is_valid())
            self.assertIn('already connected to a provider network', str(form.errors))
        finally:
            # Clean up: remove provider network connection
            circuit_term.termination_type = None
            circuit_term.termination_id = None
            circuit_term.save()

    def test_multiple_parents_without_site(self):
        """Test error when multiple parent objects are found without site scoping."""
        # Device-A1 exists in both site_a and site_b
        # Try to find device without specifying site
        form = CableImportForm(data={
            'side_a_site': '',  # Empty site - should cause multiple matches
            'side_a_parent': 'Device-A1',
            'side_a_type': 'dcim.interface',
            'side_a_name': 'eth0',
            'side_b_site': 'Site A',
            'side_b_parent': 'Device-A2',
            'side_b_type': 'dcim.interface',
            'side_b_name': 'eth0',
            'type': CableTypeChoices.TYPE_CAT6,
            'status': 'connected',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Multiple Device objects found', str(form.errors))
