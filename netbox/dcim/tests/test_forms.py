from django.test import TestCase

from dcim.choices import (
    DeviceFaceChoices,
    DeviceStatusChoices,
    InterfaceModeChoices,
    InterfaceTypeChoices,
    PortTypeChoices,
    PowerOutletStatusChoices,
)
from dcim.forms import *
from dcim.models import *
from ipam.models import ASN, RIR, VLAN
from utilities.forms.rendering import M2MAddRemoveFields
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
            'positions': 1,
            'rear_ports': [f'{rear_port.pk}:1' for rear_port in self.rear_ports],
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
            'positions': 1,
            'rear_ports': [f'{rear_port.pk}:1' for rear_port in self.rear_ports],
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


class SiteFormTestCase(TestCase):
    """
    Tests for M2MAddRemoveFields using Site ASN assignments as the test case.
    Covers both simple mode (single multi-select field) and add/remove mode (dual fields).
    """

    @classmethod
    def setUpTestData(cls):
        cls.rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        # Create 110 ASNs: 100 to pre-assign (triggering add/remove mode) plus 10 extras
        ASN.objects.bulk_create([ASN(asn=i, rir=cls.rir) for i in range(1, 111)])
        cls.asns = list(ASN.objects.order_by('asn'))

    def _site_data(self, **kwargs):
        data = {'name': 'Test Site', 'slug': 'test-site', 'status': 'active'}
        data.update(kwargs)
        return data

    def test_new_site_uses_simple_mode(self):
        """A form for a new site uses the single 'asns' field (simple mode)."""
        form = SiteForm(data=self._site_data())
        self.assertIn('asns', form.fields)
        self.assertNotIn('add_asns', form.fields)
        self.assertNotIn('remove_asns', form.fields)

    def test_existing_site_below_threshold_uses_simple_mode(self):
        """A form for an existing site with fewer than THRESHOLD ASNs uses simple mode."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.asns.set(self.asns[:5])
        form = SiteForm(instance=site)
        self.assertIn('asns', form.fields)
        self.assertNotIn('add_asns', form.fields)
        self.assertNotIn('remove_asns', form.fields)

    def test_existing_site_at_threshold_uses_add_remove_mode(self):
        """A form for an existing site with THRESHOLD or more ASNs uses add/remove mode."""
        site = Site.objects.create(name='Site 2', slug='site-2')
        site.asns.set(self.asns[:M2MAddRemoveFields.THRESHOLD])
        form = SiteForm(instance=site)
        self.assertNotIn('asns', form.fields)
        self.assertIn('add_asns', form.fields)
        self.assertIn('remove_asns', form.fields)

    def test_simple_mode_assigns_asns_on_create(self):
        """Saving a new site via simple mode assigns the selected ASNs."""
        asn_pks = [asn.pk for asn in self.asns[:3]]
        form = SiteForm(data=self._site_data(asns=asn_pks))
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.asns.values_list('pk', flat=True)), set(asn_pks))

    def test_simple_mode_replaces_asns_on_edit(self):
        """Saving an existing site via simple mode replaces the current ASN assignments."""
        site = Site.objects.create(name='Site 3', slug='site-3')
        site.asns.set(self.asns[:3])
        new_asn_pks = [asn.pk for asn in self.asns[3:6]]
        form = SiteForm(
            data=self._site_data(name='Site 3', slug='site-3', asns=new_asn_pks),
            instance=site
        )
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.asns.values_list('pk', flat=True)), set(new_asn_pks))

    def test_add_remove_mode_adds_asns(self):
        """In add/remove mode, specifying 'add_asns' appends to current assignments."""
        site = Site.objects.create(name='Site 4', slug='site-4')
        site.asns.set(self.asns[:M2MAddRemoveFields.THRESHOLD])
        new_asn_pks = [asn.pk for asn in self.asns[M2MAddRemoveFields.THRESHOLD:]]
        form = SiteForm(
            data=self._site_data(name='Site 4', slug='site-4', add_asns=new_asn_pks),
            instance=site
        )
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.asns.count(), len(self.asns))

    def test_add_remove_mode_removes_asns(self):
        """In add/remove mode, specifying 'remove_asns' drops those assignments."""
        site = Site.objects.create(name='Site 5', slug='site-5')
        site.asns.set(self.asns[:M2MAddRemoveFields.THRESHOLD])
        remove_pks = [asn.pk for asn in self.asns[:5]]
        form = SiteForm(
            data=self._site_data(name='Site 5', slug='site-5', remove_asns=remove_pks),
            instance=site
        )
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.asns.count(), M2MAddRemoveFields.THRESHOLD - 5)
        self.assertFalse(site.asns.filter(pk__in=remove_pks).exists())

    def test_add_remove_mode_simultaneous_add_and_remove(self):
        """In add/remove mode, add and remove operations are applied together."""
        site = Site.objects.create(name='Site 6', slug='site-6')
        site.asns.set(self.asns[:M2MAddRemoveFields.THRESHOLD])
        add_pks = [asn.pk for asn in self.asns[M2MAddRemoveFields.THRESHOLD:M2MAddRemoveFields.THRESHOLD + 3]]
        remove_pks = [asn.pk for asn in self.asns[:3]]
        form = SiteForm(
            data=self._site_data(name='Site 6', slug='site-6', add_asns=add_pks, remove_asns=remove_pks),
            instance=site
        )
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.asns.count(), M2MAddRemoveFields.THRESHOLD)
        self.assertTrue(site.asns.filter(pk__in=add_pks).count() == 3)
        self.assertFalse(site.asns.filter(pk__in=remove_pks).exists())
