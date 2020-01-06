from django.test import TestCase

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Region, Site
from ipam.constants import *
from ipam.filters import AggregateFilter, IPAddressFilter, PrefixFilter, RIRFilter, RoleFilter, VLANFilter, VRFFilter
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VRF
from virtualization.models import Cluster, ClusterType, VirtualMachine


class VRFTestCase(TestCase):
    queryset = VRF.objects.all()

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:100', enforce_unique=False),
            VRF(name='VRF 2', rd='65000:200', enforce_unique=False),
            VRF(name='VRF 3', rd='65000:300', enforce_unique=False),
            VRF(name='VRF 4', rd='65000:400', enforce_unique=True),
            VRF(name='VRF 5', rd='65000:500', enforce_unique=True),
            VRF(name='VRF 6', rd='65000:600', enforce_unique=True),
        )
        VRF.objects.bulk_create(vrfs)

    def test_name(self):
        params = {'name': ['VRF 1', 'VRF 2']}
        self.assertEqual(VRFFilter(params, self.queryset).qs.count(), 2)

    def test_rd(self):
        params = {'rd': ['65000:100', '65000:200']}
        self.assertEqual(VRFFilter(params, self.queryset).qs.count(), 2)

    def test_enforce_unique(self):
        params = {'enforce_unique': 'true'}
        self.assertEqual(VRFFilter(params, self.queryset).qs.count(), 3)
        params = {'enforce_unique': 'false'}
        self.assertEqual(VRFFilter(params, self.queryset).qs.count(), 3)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(VRFFilter(params, self.queryset).qs.count(), 3)


class RIRTestCase(TestCase):
    queryset = RIR.objects.all()

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1', is_private=False),
            RIR(name='RIR 2', slug='rir-2', is_private=False),
            RIR(name='RIR 3', slug='rir-3', is_private=False),
            RIR(name='RIR 4', slug='rir-4', is_private=True),
            RIR(name='RIR 5', slug='rir-5', is_private=True),
            RIR(name='RIR 6', slug='rir-6', is_private=True),
        )
        RIR.objects.bulk_create(rirs)

    def test_name(self):
        params = {'name': ['RIR 1', 'RIR 2']}
        self.assertEqual(RIRFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rir-1', 'rir-2']}
        self.assertEqual(RIRFilter(params, self.queryset).qs.count(), 2)

    def test_is_private(self):
        params = {'is_private': 'true'}
        self.assertEqual(RIRFilter(params, self.queryset).qs.count(), 3)
        params = {'is_private': 'false'}
        self.assertEqual(RIRFilter(params, self.queryset).qs.count(), 3)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(RIRFilter(params, self.queryset).qs.count(), 3)


class AggregateTestCase(TestCase):
    queryset = Aggregate.objects.all()

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        )
        RIR.objects.bulk_create(rirs)

        aggregates = (
            Aggregate(family=4, prefix='10.1.0.0/16', rir=rirs[0], date_added='2020-01-01'),
            Aggregate(family=4, prefix='10.2.0.0/16', rir=rirs[0], date_added='2020-01-02'),
            Aggregate(family=4, prefix='10.3.0.0/16', rir=rirs[1], date_added='2020-01-03'),
            Aggregate(family=6, prefix='2001:db8:1::/48', rir=rirs[1], date_added='2020-01-04'),
            Aggregate(family=6, prefix='2001:db8:2::/48', rir=rirs[2], date_added='2020-01-05'),
            Aggregate(family=6, prefix='2001:db8:3::/48', rir=rirs[2], date_added='2020-01-06'),
        )
        Aggregate.objects.bulk_create(aggregates)

    def test_family(self):
        params = {'family': '4'}
        self.assertEqual(AggregateFilter(params, self.queryset).qs.count(), 3)

    def test_date_added(self):
        params = {'date_added': ['2020-01-01', '2020-01-02']}
        self.assertEqual(AggregateFilter(params, self.queryset).qs.count(), 2)

    # TODO: Test for multiple values
    def test_prefix(self):
        params = {'prefix': '10.1.0.0/16'}
        self.assertEqual(AggregateFilter(params, self.queryset).qs.count(), 1)

    def test_rir(self):
        rirs = RIR.objects.all()[:2]
        params = {'rir_id': [rirs[0].pk, rirs[1].pk]}
        self.assertEqual(AggregateFilter(params, self.queryset).qs.count(), 4)
        params = {'rir': [rirs[0].slug, rirs[1].slug]}
        self.assertEqual(AggregateFilter(params, self.queryset).qs.count(), 4)


class RoleTestCase(TestCase):
    queryset = Role.objects.all()

    @classmethod
    def setUpTestData(cls):

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RoleFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Role 1', 'Role 2']}
        self.assertEqual(RoleFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['role-1', 'role-2']}
        self.assertEqual(RoleFilter(params, self.queryset).qs.count(), 2)


class PrefixTestCase(TestCase):
    queryset = Prefix.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        # Can't use bulk_create for models with MPTT fields
        for r in regions:
            r.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        vrfs = (
            VRF(name='VRF 1', rd='65000:100'),
            VRF(name='VRF 2', rd='65000:200'),
            VRF(name='VRF 3', rd='65000:300'),
        )
        VRF.objects.bulk_create(vrfs)

        vlans = (
            VLAN(vid=1, name='VLAN 1'),
            VLAN(vid=2, name='VLAN 2'),
            VLAN(vid=3, name='VLAN 3'),
        )
        VLAN.objects.bulk_create(vlans)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

        prefixes = (
            Prefix(family=4, prefix='10.0.0.0/24', site=None, vrf=None, vlan=None, role=None, is_pool=True),
            Prefix(family=4, prefix='10.0.1.0/24', site=sites[0], vrf=vrfs[0], vlan=vlans[0], role=roles[0]),
            Prefix(family=4, prefix='10.0.2.0/24', site=sites[1], vrf=vrfs[1], vlan=vlans[1], role=roles[1], status=PREFIX_STATUS_DEPRECATED),
            Prefix(family=4, prefix='10.0.3.0/24', site=sites[2], vrf=vrfs[2], vlan=vlans[2], role=roles[2], status=PREFIX_STATUS_RESERVED),
            Prefix(family=6, prefix='2001:db8::/64', site=None, vrf=None, vlan=None, role=None, is_pool=True),
            Prefix(family=6, prefix='2001:db8:0:1::/64', site=sites[0], vrf=vrfs[0], vlan=vlans[0], role=roles[0]),
            Prefix(family=6, prefix='2001:db8:0:2::/64', site=sites[1], vrf=vrfs[1], vlan=vlans[1], role=roles[1], status=PREFIX_STATUS_DEPRECATED),
            Prefix(family=6, prefix='2001:db8:0:3::/64', site=sites[2], vrf=vrfs[2], vlan=vlans[2], role=roles[2], status=PREFIX_STATUS_RESERVED),
            Prefix(family=4, prefix='10.0.0.0/16'),
            Prefix(family=6, prefix='2001:db8::/32'),
        )
        Prefix.objects.bulk_create(prefixes)

    def test_family(self):
        params = {'family': '6'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 5)

    def test_is_pool(self):
        params = {'is_pool': 'true'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 2)
        params = {'is_pool': 'false'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 8)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 3)

    def test_within(self):
        params = {'within': '10.0.0.0/16'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_within_include(self):
        params = {'within_include': '10.0.0.0/16'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 5)

    def test_contains(self):
        params = {'contains': '10.0.1.0/24'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 2)
        params = {'contains': '2001:db8:0:1::/64'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 2)

    def test_mask_length(self):
        params = {'mask_length': '24'}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)
        params = {'vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_vlan(self):
        vlans = VLAN.objects.all()[:2]
        params = {'vlan_id': [vlans[0].pk, vlans[1].pk]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)
        # TODO: Test for multiple values
        params = {'vlan_vid': vlans[0].vid}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = Role.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {'status': [PREFIX_STATUS_DEPRECATED, PREFIX_STATUS_RESERVED]}
        self.assertEqual(PrefixFilter(params, self.queryset).qs.count(), 4)


class IPAddressTestCase(TestCase):
    queryset = IPAddress.objects.all()

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:100'),
            VRF(name='VRF 2', rd='65000:200'),
            VRF(name='VRF 3', rd='65000:300'),
        )
        VRF.objects.bulk_create(vrfs)

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(device_type=device_type, name='Device 1', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 2', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 3', site=site, device_role=device_role),
        )
        Device.objects.bulk_create(devices)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster = Cluster.objects.create(type=clustertype, name='Cluster 1')

        virtual_machines = (
            VirtualMachine(name='Virtual Machine 1', cluster=cluster),
            VirtualMachine(name='Virtual Machine 2', cluster=cluster),
            VirtualMachine(name='Virtual Machine 3', cluster=cluster),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        interfaces = (
            Interface(device=devices[0], name='Interface 1'),
            Interface(device=devices[1], name='Interface 2'),
            Interface(device=devices[2], name='Interface 3'),
            Interface(virtual_machine=virtual_machines[0], name='Interface 1'),
            Interface(virtual_machine=virtual_machines[1], name='Interface 2'),
            Interface(virtual_machine=virtual_machines[2], name='Interface 3'),
        )
        Interface.objects.bulk_create(interfaces)

        ipaddresses = (
            IPAddress(family=4, address='10.0.0.1/24', vrf=None, interface=None, status=IPADDRESS_STATUS_ACTIVE, role=None, dns_name='ipaddress-a'),
            IPAddress(family=4, address='10.0.0.2/24', vrf=vrfs[0], interface=interfaces[0], status=IPADDRESS_STATUS_ACTIVE, role=None, dns_name='ipaddress-b'),
            IPAddress(family=4, address='10.0.0.3/24', vrf=vrfs[1], interface=interfaces[1], status=IPADDRESS_STATUS_RESERVED, role=IPADDRESS_ROLE_VIP, dns_name='ipaddress-c'),
            IPAddress(family=4, address='10.0.0.4/24', vrf=vrfs[2], interface=interfaces[2], status=IPADDRESS_STATUS_DEPRECATED, role=IPADDRESS_ROLE_SECONDARY, dns_name='ipaddress-d'),
            IPAddress(family=6, address='2001:db8::1/64', vrf=None, interface=None, status=IPADDRESS_STATUS_ACTIVE, role=None, dns_name='ipaddress-a'),
            IPAddress(family=6, address='2001:db8::2/64', vrf=vrfs[0], interface=interfaces[3], status=IPADDRESS_STATUS_ACTIVE, role=None, dns_name='ipaddress-b'),
            IPAddress(family=6, address='2001:db8::3/64', vrf=vrfs[1], interface=interfaces[4], status=IPADDRESS_STATUS_RESERVED, role=IPADDRESS_ROLE_VIP, dns_name='ipaddress-c'),
            IPAddress(family=6, address='2001:db8::4/64', vrf=vrfs[2], interface=interfaces[5], status=IPADDRESS_STATUS_DEPRECATED, role=IPADDRESS_ROLE_SECONDARY, dns_name='ipaddress-d'),
        )
        IPAddress.objects.bulk_create(ipaddresses)

    def test_family(self):
        params = {'family': '6'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def test_dns_name(self):
        params = {'dns_name': ['ipaddress-a', 'ipaddress-b']}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 3)

    def test_parent(self):
        params = {'parent': '10.0.0.0/24'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)
        params = {'parent': '2001:db8::/64'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def filter_address(self):
        # Check IPv4 and IPv6, with and without a mask
        params = {'address': '10.0.0.1/24'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)
        params = {'address': '10.0.0.1'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)
        params = {'address': '2001:db8::1/64'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)
        params = {'address': '2001:db8::1'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)

    def test_mask_length(self):
        params = {'mask_length': '24'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def test_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)
        params = {'vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    # TODO: Test for multiple values
    def test_device(self):
        device = Device.objects.first()
        params = {'device_id': device.pk}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)
        params = {'device': device.name}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 1)

    def test_virtual_machine(self):
        vms = VirtualMachine.objects.all()[:2]
        params = {'virtual_machine_id': [vms[0].pk, vms[1].pk]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 2)
        params = {'virtual_machine': [vms[0].name, vms[1].name]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 2)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 2)
        params = {'interface': ['Interface 1', 'Interface 2']}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def test_assigned_to_interface(self):
        params = {'assigned_to_interface': 'true'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 6)
        params = {'assigned_to_interface': 'false'}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [PREFIX_STATUS_DEPRECATED, PREFIX_STATUS_RESERVED]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)

    def test_role(self):
        params = {'role': [IPADDRESS_ROLE_SECONDARY, IPADDRESS_ROLE_VIP]}
        self.assertEqual(IPAddressFilter(params, self.queryset).qs.count(), 4)
