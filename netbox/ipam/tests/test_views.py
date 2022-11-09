import datetime

from django.test import override_settings
from django.urls import reverse
from netaddr import IPNetwork

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Interface
from ipam.choices import *
from ipam.models import *
from tenancy.models import Tenant
from utilities.testing import ViewTestCases, create_test_device, create_tags


class ASNTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ASN

    @classmethod
    def setUpTestData(cls):

        rirs = [
            RIR.objects.create(name='RFC 6996', slug='rfc-6996', description='Private Use', is_private=True),
            RIR.objects.create(name='RFC 7300', slug='rfc-7300', description='IANA Use', is_private=True),
        ]
        sites = [
            Site.objects.create(name='Site 1', slug='site-1'),
            Site.objects.create(name='Site 2', slug='site-2')
        ]
        tenants = [
            Tenant.objects.create(name='Tenant 1', slug='tenant-1'),
            Tenant.objects.create(name='Tenant 2', slug='tenant-2'),
        ]

        asns = (
            ASN(asn=64513, rir=rirs[0], tenant=tenants[0]),
            ASN(asn=65535, rir=rirs[1], tenant=tenants[1]),
            ASN(asn=4200000000, rir=rirs[0], tenant=tenants[0]),
            ASN(asn=4200002301, rir=rirs[1], tenant=tenants[1]),
        )
        ASN.objects.bulk_create(asns)

        asns[0].sites.set([sites[0]])
        asns[1].sites.set([sites[1]])
        asns[2].sites.set([sites[0]])
        asns[3].sites.set([sites[1]])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'asn': 64512,
            'rir': rirs[0].pk,
            'tenant': tenants[0].pk,
            'site': sites[0].pk,
            'description': 'A new ASN',
        }

        cls.csv_data = (
            "asn,rir",
            "64533,RFC 6996",
            "64523,RFC 6996",
            "4200000002,RFC 6996",
        )

        cls.csv_update_data = (
            "id,description",
            f"{asns[0].pk},New description1",
            f"{asns[1].pk},New description2",
            f"{asns[2].pk},New description3",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'description': 'Next description',
        }


class VRFTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VRF

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant A', slug='tenant-a'),
            Tenant(name='Tenant B', slug='tenant-b'),
        )
        Tenant.objects.bulk_create(tenants)

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        )
        VRF.objects.bulk_create(vrfs)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'VRF X',
            'rd': '65000:999',
            'tenant': tenants[0].pk,
            'enforce_unique': True,
            'description': 'A new VRF',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name",
            "VRF 4",
            "VRF 5",
            "VRF 6",
        )

        cls.csv_update_data = (
            "id,name",
            f"{vrfs[0].pk},VRF 7",
            f"{vrfs[1].pk},VRF 8",
            f"{vrfs[2].pk},VRF 9",
        )

        cls.bulk_edit_data = {
            'tenant': tenants[1].pk,
            'enforce_unique': False,
            'description': 'New description',
        }


class RouteTargetTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = RouteTarget

    @classmethod
    def setUpTestData(cls):

        tenants = (
            Tenant(name='Tenant A', slug='tenant-a'),
            Tenant(name='Tenant B', slug='tenant-b'),
        )
        Tenant.objects.bulk_create(tenants)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        route_targets = (
            RouteTarget(name='65000:1001', tenant=tenants[0]),
            RouteTarget(name='65000:1002', tenant=tenants[1]),
            RouteTarget(name='65000:1003'),
        )
        RouteTarget.objects.bulk_create(route_targets)

        cls.form_data = {
            'name': '65000:100',
            'description': 'A new route target',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,tenant,description",
            "65000:1004,Tenant A,Foo",
            "65000:1005,Tenant B,Bar",
            "65000:1006,,No tenant",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{route_targets[0].pk},65000:1007,New description1",
            f"{route_targets[1].pk},65000:1008,New description2",
            f"{route_targets[2].pk},65000:1009,New description3",
        )

        cls.bulk_edit_data = {
            'tenant': tenants[1].pk,
            'description': 'New description',
        }


class RIRTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = RIR

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        )
        RIR.objects.bulk_create(rirs)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'RIR X',
            'slug': 'rir-x',
            'is_private': True,
            'description': 'A new RIR',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "RIR 4,rir-4,Fourth RIR",
            "RIR 5,rir-5,Fifth RIR",
            "RIR 6,rir-6,Sixth RIR",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{rirs[0].pk},RIR 7,Fourth RIR7",
            f"{rirs[1].pk},RIR 8,Fifth RIR8",
            f"{rirs[2].pk},RIR 9,Sixth RIR9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class AggregateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Aggregate

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
        )
        RIR.objects.bulk_create(rirs)

        aggregates = (
            Aggregate(prefix=IPNetwork('10.1.0.0/16'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('10.2.0.0/16'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('10.3.0.0/16'), rir=rirs[0]),
        )
        Aggregate.objects.bulk_create(aggregates)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'prefix': IPNetwork('10.99.0.0/16'),
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'A new aggregate',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "prefix,rir",
            "10.4.0.0/16,RIR 1",
            "10.5.0.0/16,RIR 1",
            "10.6.0.0/16,RIR 1",
        )

        cls.csv_update_data = (
            "id,description",
            f"{aggregates[0].pk},New description1",
            f"{aggregates[1].pk},New description2",
            f"{aggregates[2].pk},New description3",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'New description',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_aggregate_prefixes(self):
        rir = RIR.objects.first()
        aggregate = Aggregate.objects.create(prefix=IPNetwork('192.168.0.0/16'), rir=rir)
        prefixes = (
            Prefix(prefix=IPNetwork('192.168.1.0/24')),
            Prefix(prefix=IPNetwork('192.168.2.0/24')),
            Prefix(prefix=IPNetwork('192.168.3.0/24')),
        )
        Prefix.objects.bulk_create(prefixes)
        self.assertEqual(aggregate.get_child_prefixes().count(), 3)

        url = reverse('ipam:aggregate_prefixes', kwargs={'pk': aggregate.pk})
        self.assertHttpStatus(self.client.get(url), 200)


class RoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Role

    @classmethod
    def setUpTestData(cls):

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Role X',
            'slug': 'role-x',
            'weight': 200,
            'description': 'A new role',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,weight",
            "Role 4,role-4,1000",
            "Role 5,role-5,1000",
            "Role 6,role-6,1000",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{roles[0].pk},Role 7,New description7",
            f"{roles[1].pk},Role 8,New description8",
            f"{roles[2].pk},Role 9,New description9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class PrefixTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Prefix

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        prefixes = (
            Prefix(prefix=IPNetwork('10.1.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
            Prefix(prefix=IPNetwork('10.2.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
            Prefix(prefix=IPNetwork('10.3.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
        )
        Prefix.objects.bulk_create(prefixes)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'prefix': IPNetwork('192.0.2.0/24'),
            'site': sites[1].pk,
            'vrf': vrfs[1].pk,
            'tenant': None,
            'vlan': None,
            'status': PrefixStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': True,
            'description': 'A new prefix',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vrf,prefix,status",
            "VRF 1,10.4.0.0/16,active",
            "VRF 1,10.5.0.0/16,active",
            "VRF 1,10.6.0.0/16,active",
        )

        cls.csv_update_data = (
            "id,description,status",
            f"{prefixes[0].pk},New description 7,{PrefixStatusChoices.STATUS_RESERVED}",
            f"{prefixes[1].pk},New description 8,{PrefixStatusChoices.STATUS_RESERVED}",
            f"{prefixes[2].pk},New description 9,{PrefixStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': PrefixStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': False,
            'description': 'New description',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_prefix_prefixes(self):
        prefixes = (
            Prefix(prefix=IPNetwork('192.168.0.0/16')),
            Prefix(prefix=IPNetwork('192.168.1.0/24')),
            Prefix(prefix=IPNetwork('192.168.2.0/24')),
            Prefix(prefix=IPNetwork('192.168.3.0/24')),
        )
        Prefix.objects.bulk_create(prefixes)
        self.assertEqual(prefixes[0].get_child_prefixes().count(), 3)

        url = reverse('ipam:prefix_prefixes', kwargs={'pk': prefixes[0].pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_prefix_ipranges(self):
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/16'))
        ip_ranges = (
            IPRange(start_address='192.168.0.1/24', end_address='192.168.0.100/24', size=99),
            IPRange(start_address='192.168.1.1/24', end_address='192.168.1.100/24', size=99),
            IPRange(start_address='192.168.2.1/24', end_address='192.168.2.100/24', size=99),
        )
        IPRange.objects.bulk_create(ip_ranges)
        self.assertEqual(prefix.get_child_ranges().count(), 3)

        url = reverse('ipam:prefix_ipranges', kwargs={'pk': prefix.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_prefix_ipaddresses(self):
        prefix = Prefix.objects.create(prefix=IPNetwork('192.168.0.0/16'))
        ip_addresses = (
            IPAddress(address=IPNetwork('192.168.0.1/16')),
            IPAddress(address=IPNetwork('192.168.0.2/16')),
            IPAddress(address=IPNetwork('192.168.0.3/16')),
        )
        IPAddress.objects.bulk_create(ip_addresses)
        self.assertEqual(prefix.get_child_ips().count(), 3)

        url = reverse('ipam:prefix_ipaddresses', kwargs={'pk': prefix.pk})
        self.assertHttpStatus(self.client.get(url), 200)


class IPRangeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPRange

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        ip_ranges = (
            IPRange(start_address='192.168.0.10/24', end_address='192.168.0.100/24', size=91),
            IPRange(start_address='192.168.1.10/24', end_address='192.168.1.100/24', size=91),
            IPRange(start_address='192.168.2.10/24', end_address='192.168.2.100/24', size=91),
            IPRange(start_address='192.168.3.10/24', end_address='192.168.3.100/24', size=91),
            IPRange(start_address='192.168.4.10/24', end_address='192.168.4.100/24', size=91),
        )
        IPRange.objects.bulk_create(ip_ranges)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'start_address': IPNetwork('192.0.5.10/24'),
            'end_address': IPNetwork('192.0.5.100/24'),
            'vrf': vrfs[1].pk,
            'tenant': None,
            'vlan': None,
            'status': IPRangeStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'is_pool': True,
            'description': 'A new IP range',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vrf,start_address,end_address,status",
            "VRF 1,10.1.0.1/16,10.1.9.254/16,active",
            "VRF 1,10.2.0.1/16,10.2.9.254/16,active",
            "VRF 1,10.3.0.1/16,10.3.9.254/16,active",
        )

        cls.csv_update_data = (
            "id,description,status",
            f"{ip_ranges[0].pk},New description 7,{IPRangeStatusChoices.STATUS_RESERVED}",
            f"{ip_ranges[1].pk},New description 8,{IPRangeStatusChoices.STATUS_RESERVED}",
            f"{ip_ranges[2].pk},New description 9,{IPRangeStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': IPRangeStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'New description',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_iprange_ipaddresses(self):
        iprange = IPRange.objects.create(
            start_address=IPNetwork('192.168.0.1/24'),
            end_address=IPNetwork('192.168.0.100/24'),
            size=99
        )
        ip_addresses = (
            IPAddress(address=IPNetwork('192.168.0.1/24')),
            IPAddress(address=IPNetwork('192.168.0.2/24')),
            IPAddress(address=IPNetwork('192.168.0.3/24')),
        )
        IPAddress.objects.bulk_create(ip_addresses)
        self.assertEqual(iprange.get_child_ips().count(), 3)

        url = reverse('ipam:iprange_ipaddresses', kwargs={'pk': iprange.pk})
        self.assertHttpStatus(self.client.get(url), 200)


class IPAddressTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = IPAddress

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )
        VRF.objects.bulk_create(vrfs)

        ipaddresses = (
            IPAddress(address=IPNetwork('192.0.2.1/24'), vrf=vrfs[0]),
            IPAddress(address=IPNetwork('192.0.2.2/24'), vrf=vrfs[0]),
            IPAddress(address=IPNetwork('192.0.2.3/24'), vrf=vrfs[0]),
        )
        IPAddress.objects.bulk_create(ipaddresses)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'vrf': vrfs[1].pk,
            'address': IPNetwork('192.0.2.99/24'),
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'nat_inside': None,
            'dns_name': 'example',
            'description': 'A new IP address',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vrf,address,status",
            "VRF 1,192.0.2.4/24,active",
            "VRF 1,192.0.2.5/24,active",
            "VRF 1,192.0.2.6/24,active",
        )

        cls.csv_update_data = (
            "id,description,status",
            f"{ipaddresses[0].pk},New description 7,{IPAddressStatusChoices.STATUS_RESERVED}",
            f"{ipaddresses[1].pk},New description 8,{IPAddressStatusChoices.STATUS_RESERVED}",
            f"{ipaddresses[2].pk},New description 9,{IPAddressStatusChoices.STATUS_RESERVED}",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'dns_name': 'example',
            'description': 'New description',
        }


class FHRPGroupTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = FHRPGroup

    @classmethod
    def setUpTestData(cls):

        fhrp_groups = (
            FHRPGroup(protocol=FHRPGroupProtocolChoices.PROTOCOL_VRRP2, group_id=10, auth_type=FHRPGroupAuthTypeChoices.AUTHENTICATION_PLAINTEXT, auth_key='foobar123'),
            FHRPGroup(protocol=FHRPGroupProtocolChoices.PROTOCOL_VRRP3, group_id=20, auth_type=FHRPGroupAuthTypeChoices.AUTHENTICATION_MD5, auth_key='foobar123'),
            FHRPGroup(protocol=FHRPGroupProtocolChoices.PROTOCOL_HSRP, group_id=30),
        )
        FHRPGroup.objects.bulk_create(fhrp_groups)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'protocol': FHRPGroupProtocolChoices.PROTOCOL_VRRP2,
            'group_id': 99,
            'auth_type': FHRPGroupAuthTypeChoices.AUTHENTICATION_MD5,
            'auth_key': 'abc123def456',
            'description': 'Blah blah blah',
            'name': 'test123 name',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "protocol,group_id,auth_type,auth_key,description",
            "vrrp2,40,plaintext,foobar123,Foo",
            "vrrp3,50,md5,foobar123,Bar",
            "hsrp,60,,,",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{fhrp_groups[0].pk},FHRP Group 1,New description 1",
            f"{fhrp_groups[1].pk},FHRP Group 2,New description 2",
            f"{fhrp_groups[2].pk},FHRP Group 3,New description 3",
        )

        cls.bulk_edit_data = {
            'protocol': FHRPGroupProtocolChoices.PROTOCOL_CARP,
        }


class VLANGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = VLANGroup

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vlan_groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sites[0]),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', scope=sites[0]),
        )
        VLANGroup.objects.bulk_create(vlan_groups)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'VLAN Group X',
            'slug': 'vlan-group-x',
            'min_vid': 1,
            'max_vid': 4094,
            'description': 'A new VLAN group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            f"name,slug,scope_type,scope_id,description",
            f"VLAN Group 4,vlan-group-4,,,Fourth VLAN group",
            f"VLAN Group 5,vlan-group-5,dcim.site,{sites[0].pk},Fifth VLAN group",
            f"VLAN Group 6,vlan-group-6,dcim.site,{sites[1].pk},Sixth VLAN group",
        )

        cls.csv_update_data = (
            f"id,name,description",
            f"{vlan_groups[0].pk},VLAN Group 7,Fourth VLAN group7",
            f"{vlan_groups[1].pk},VLAN Group 8,Fifth VLAN group8",
            f"{vlan_groups[2].pk},VLAN Group 9,Sixth VLAN group9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class VLANTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VLAN

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vlangroups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sites[1]),
        )
        VLANGroup.objects.bulk_create(vlangroups)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        vlans = (
            VLAN(group=vlangroups[0], vid=101, name='VLAN101', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=102, name='VLAN102', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=103, name='VLAN103', site=sites[0], role=roles[0]),
        )
        VLAN.objects.bulk_create(vlans)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'vid': 999,
            'name': 'VLAN999',
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'A new VLAN',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "vid,name,status",
            "104,VLAN104,active",
            "105,VLAN105,active",
            "106,VLAN106,active",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{vlans[0].pk},VLAN107,New description 7",
            f"{vlans[1].pk},VLAN108,New description 8",
            f"{vlans[2].pk},VLAN109,New description 9",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'New description',
        }


class ServiceTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ServiceTemplate

    @classmethod
    def setUpTestData(cls):
        service_templates = (
            ServiceTemplate(name='Service Template 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[101]),
            ServiceTemplate(name='Service Template 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[102]),
            ServiceTemplate(name='Service Template 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[103]),
        )
        ServiceTemplate.objects.bulk_create(service_templates)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Service Template X',
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '104,105',
            'description': 'A new service template',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,protocol,ports,description",
            "Service Template 4,tcp,1,First service template",
            "Service Template 5,tcp,2,Second service template",
            "Service Template 6,tcp,3,Third service template",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{service_templates[0].pk},Service Template 7,First service template7",
            f"{service_templates[1].pk},Service Template 8,Second service template8",
            f"{service_templates[2].pk},Service Template 9,Third service template9",
        )

        cls.bulk_edit_data = {
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '106,107',
            'description': 'New description',
        }


class ServiceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Service

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        device = Device.objects.create(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)

        services = (
            Service(device=device, name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[101]),
            Service(device=device, name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[102]),
            Service(device=device, name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[103]),
        )
        Service.objects.bulk_create(services)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'virtual_machine': None,
            'name': 'Service X',
            'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
            'ports': '104,105',
            'ipaddresses': [],
            'description': 'A new service',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "device,name,protocol,ports,description",
            "Device 1,Service 1,tcp,1,First service",
            "Device 1,Service 2,tcp,2,Second service",
            "Device 1,Service 3,udp,3,Third service",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{services[0].pk},Service 7,First service7",
            f"{services[1].pk},Service 8,Second service8",
            f"{services[2].pk},Service 9,Third service9",
        )

        cls.bulk_edit_data = {
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'ports': '106,107',
            'description': 'New description',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_create_from_template(self):
        self.add_permissions('ipam.add_service')

        device = Device.objects.first()
        service_template = ServiceTemplate.objects.create(
            name='HTTP',
            protocol=ServiceProtocolChoices.PROTOCOL_TCP,
            ports=[80],
            description='Hypertext transfer protocol'
        )

        request = {
            'path': self._get_url('add'),
            'data': {
                'device': device.pk,
                'service_template': service_template.pk,
            },
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.device, device)
        self.assertEqual(instance.name, service_template.name)
        self.assertEqual(instance.protocol, service_template.protocol)
        self.assertEqual(instance.ports, service_template.ports)
        self.assertEqual(instance.description, service_template.description)


class L2VPNTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = L2VPN

    @classmethod
    def setUpTestData(cls):
        rts = (
            RouteTarget(name='64534:123'),
            RouteTarget(name='64534:321')
        )
        RouteTarget.objects.bulk_create(rts)

        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type=L2VPNTypeChoices.TYPE_VXLAN, identifier='650001'),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type=L2VPNTypeChoices.TYPE_VXLAN, identifier='650002'),
            L2VPN(name='L2VPN 3', slug='l2vpn-3', type=L2VPNTypeChoices.TYPE_VXLAN, identifier='650003')
        )
        L2VPN.objects.bulk_create(l2vpns)

        cls.csv_data = (
            'name,slug,type,identifier',
            'L2VPN 5,l2vpn-5,vxlan,456',
            'L2VPN 6,l2vpn-6,vxlan,444',
        )

        cls.csv_update_data = (
            'id,name,description',
            f'{l2vpns[0].pk},L2VPN 7,New description 7',
            f'{l2vpns[1].pk},L2VPN 8,New description 8',
        )

        cls.bulk_edit_data = {
            'description': 'New Description',
        }

        cls.form_data = {
            'name': 'L2VPN 8',
            'slug': 'l2vpn-8',
            'type': L2VPNTypeChoices.TYPE_VXLAN,
            'identifier': 123,
            'description': 'Description',
            'import_targets': [rts[0].pk],
            'export_targets': [rts[1].pk]
        }


class L2VPNTerminationTestCase(
        ViewTestCases.GetObjectViewTestCase,
        ViewTestCases.GetObjectChangelogViewTestCase,
        ViewTestCases.CreateObjectViewTestCase,
        ViewTestCases.EditObjectViewTestCase,
        ViewTestCases.DeleteObjectViewTestCase,
        ViewTestCases.ListObjectsViewTestCase,
        ViewTestCases.BulkImportObjectsViewTestCase,
        ViewTestCases.BulkDeleteObjectsViewTestCase,
):

    model = L2VPNTermination

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        interface = Interface.objects.create(name='Interface 1', device=device, type='1000baset')
        l2vpns = (
            L2VPN(name='L2VPN 1', slug='l2vpn-1', type=L2VPNTypeChoices.TYPE_VXLAN, identifier=650001),
            L2VPN(name='L2VPN 2', slug='l2vpn-2', type=L2VPNTypeChoices.TYPE_VXLAN, identifier=650002),
        )
        L2VPN.objects.bulk_create(l2vpns)

        vlans = (
            VLAN(name='Vlan 1', vid=1001),
            VLAN(name='Vlan 2', vid=1002),
            VLAN(name='Vlan 3', vid=1003),
            VLAN(name='Vlan 4', vid=1004),
            VLAN(name='Vlan 5', vid=1005),
            VLAN(name='Vlan 6', vid=1006)
        )
        VLAN.objects.bulk_create(vlans)

        terminations = (
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[0]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[1]),
            L2VPNTermination(l2vpn=l2vpns[0], assigned_object=vlans[2])
        )
        L2VPNTermination.objects.bulk_create(terminations)

        cls.form_data = {
            'l2vpn': l2vpns[0].pk,
            'device': device.pk,
            'interface': interface.pk,
        }

        cls.csv_data = (
            "l2vpn,vlan",
            "L2VPN 1,Vlan 4",
            "L2VPN 1,Vlan 5",
            "L2VPN 1,Vlan 6",
        )

        cls.csv_update_data = (
            f"id,l2vpn",
            f"{terminations[0].pk},{l2vpns[0].name}",
            f"{terminations[1].pk},{l2vpns[0].name}",
            f"{terminations[2].pk},{l2vpns[0].name}",
        )

        cls.bulk_edit_data = {}

    #
    # Custom assertions
    #

    # TODO: Remove this
    def assertInstanceEqual(self, instance, data, exclude=None, api=False):
        """
        Override parent
        """
        if exclude is None:
            exclude = []

        fields = [k for k in data.keys() if k not in exclude]
        model_dict = self.model_to_dict(instance, fields=fields, api=api)

        # Omit any dictionary keys which are not instance attributes or have been excluded
        relevant_data = {
            k: v for k, v in data.items() if hasattr(instance, k) and k not in exclude
        }

        # Handle relations on the model
        for k, v in model_dict.items():
            if isinstance(v, object) and hasattr(v, 'first'):
                model_dict[k] = v.first().pk

        self.assertDictEqual(model_dict, relevant_data)
