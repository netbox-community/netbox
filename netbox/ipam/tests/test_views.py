import datetime

from netaddr import IPNetwork

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.choices import *
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from utilities.testing import StandardTestCases


class VRFTestCase(StandardTestCases.Views):
    model = VRF

    @classmethod
    def setUpTestData(cls):

        VRF.objects.bulk_create([
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        ])

        cls.form_data = {
            'name': 'VRF X',
            'rd': '65000:999',
            'tenant': None,
            'enforce_unique': True,
            'description': 'A new VRF',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "name",
            "VRF 4",
            "VRF 5",
            "VRF 6",
        )

        cls.bulk_edit_data = {
            'tenant': None,
            'enforce_unique': False,
            'description': 'New description',
        }


class RIRTestCase(StandardTestCases.Views):
    model = RIR

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None
    test_bulk_edit_objects = None

    @classmethod
    def setUpTestData(cls):

        RIR.objects.bulk_create([
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        ])

        cls.form_data = {
            'name': 'RIR X',
            'slug': 'rir-x',
            'is_private': True,
        }

        cls.csv_data = (
            "name,slug",
            "RIR 4,rir-4",
            "RIR 5,rir-5",
            "RIR 6,rir-6",
        )


class AggregateTestCase(StandardTestCases.Views):
    model = Aggregate

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
        )
        RIR.objects.bulk_create(rirs)

        Aggregate.objects.bulk_create([
            Aggregate(family=4, prefix=IPNetwork('10.1.0.0/16'), rir=rirs[0]),
            Aggregate(family=4, prefix=IPNetwork('10.2.0.0/16'), rir=rirs[0]),
            Aggregate(family=4, prefix=IPNetwork('10.3.0.0/16'), rir=rirs[0]),
        ])

        cls.form_data = {
            'family': 4,
            'prefix': IPNetwork('10.99.0.0/16'),
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'A new aggregate',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "prefix,rir",
            "10.4.0.0/16,RIR 1",
            "10.5.0.0/16,RIR 1",
            "10.6.0.0/16,RIR 1",
        )

        cls.bulk_edit_data = {
            'rir': rirs[1].pk,
            'date_added': datetime.date(2020, 1, 1),
            'description': 'New description',
        }


class RoleTestCase(StandardTestCases.Views):
    model = Role

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None
    test_bulk_edit_objects = None

    @classmethod
    def setUpTestData(cls):

        Role.objects.bulk_create([
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        ])

        cls.form_data = {
            'name': 'Role X',
            'slug': 'role-x',
            'weight': 200,
            'description': 'A new role',
        }

        cls.csv_data = (
            "name,slug,weight",
            "Role 4,role-4,1000",
            "Role 5,role-5,1000",
            "Role 6,role-6,1000",
        )


class PrefixTestCase(StandardTestCases.Views):
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

        Prefix.objects.bulk_create([
            Prefix(family=4, prefix=IPNetwork('10.1.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
            Prefix(family=4, prefix=IPNetwork('10.2.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
            Prefix(family=4, prefix=IPNetwork('10.3.0.0/16'), vrf=vrfs[0], site=sites[0], role=roles[0]),
        ])

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
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "prefix,status",
            "10.4.0.0/16,Active",
            "10.5.0.0/16,Active",
            "10.6.0.0/16,Active",
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


class IPAddressTestCase(StandardTestCases.Views):
    model = IPAddress

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
        )

        IPAddress.objects.bulk_create([
            IPAddress(family=4, address=IPNetwork('192.0.2.1/24'), vrf=vrfs[0]),
            IPAddress(family=4, address=IPNetwork('192.0.2.2/24'), vrf=vrfs[0]),
            IPAddress(family=4, address=IPNetwork('192.0.2.3/24'), vrf=vrfs[0]),
        ])

        cls.form_data = {
            'vrf': vrfs[1].pk,
            'address': IPNetwork('192.0.2.99/24'),
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'interface': None,
            'nat_inside': None,
            'dns_name': 'example',
            'description': 'A new IP address',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "address,status",
            "192.0.2.4/24,Active",
            "192.0.2.5/24,Active",
            "192.0.2.6/24,Active",
        )

        cls.bulk_edit_data = {
            'vrf': vrfs[1].pk,
            'tenant': None,
            'status': IPAddressStatusChoices.STATUS_RESERVED,
            'role': IPAddressRoleChoices.ROLE_ANYCAST,
            'dns_name': 'example',
            'description': 'New description',
        }


class VLANGroupTestCase(StandardTestCases.Views):
    model = VLANGroup

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None
    test_bulk_edit_objects = None

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')

        VLANGroup.objects.bulk_create([
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', site=site),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', site=site),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', site=site),
        ])

        cls.form_data = {
            'name': 'VLAN Group X',
            'slug': 'vlan-group-x',
            'site': site.pk,
        }

        cls.csv_data = (
            "name,slug",
            "VLAN Group 4,vlan-group-4",
            "VLAN Group 5,vlan-group-5",
            "VLAN Group 6,vlan-group-6",
        )


class VLANTestCase(StandardTestCases.Views):
    model = VLAN

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        vlangroups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', site=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', site=sites[1]),
        )
        VLANGroup.objects.bulk_create(vlangroups)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
        )
        Role.objects.bulk_create(roles)

        VLAN.objects.bulk_create([
            VLAN(group=vlangroups[0], vid=101, name='VLAN101', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=102, name='VLAN102', site=sites[0], role=roles[0]),
            VLAN(group=vlangroups[0], vid=103, name='VLAN103', site=sites[0], role=roles[0]),
        ])

        cls.form_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'vid': 999,
            'name': 'VLAN999',
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'A new VLAN',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "vid,name,status",
            "104,VLAN104,Active",
            "105,VLAN105,Active",
            "106,VLAN106,Active",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'group': vlangroups[1].pk,
            'tenant': None,
            'status': VLANStatusChoices.STATUS_RESERVED,
            'role': roles[1].pk,
            'description': 'New description',
        }


class ServiceTestCase(StandardTestCases.Views):
    model = Service

    # Disable inapplicable tests
    test_import_objects = None

    # TODO: Resolve URL for Service creation
    test_create_object = None

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        device = Device.objects.create(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)

        Service.objects.bulk_create([
            Service(device=device, name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=101),
            Service(device=device, name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=102),
            Service(device=device, name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=103),
        ])

        cls.form_data = {
            'device': device.pk,
            'virtual_machine': None,
            'name': 'Service X',
            'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
            'port': 999,
            'ipaddresses': [],
            'description': 'A new service',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'protocol': ServiceProtocolChoices.PROTOCOL_UDP,
            'port': 888,
            'description': 'New description',
        }
