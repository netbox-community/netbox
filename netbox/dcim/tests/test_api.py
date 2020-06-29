from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.choices import *
from dcim.constants import *
from dcim.models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerFeed, PowerPort, PowerPortTemplate, PowerOutlet, PowerOutletTemplate, PowerPanel,
    Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site, VirtualChassis,
)
from ipam.models import VLAN
from extras.models import Graph
from utilities.testing import APITestCase, APIViewTestCases
from virtualization.models import Cluster, ClusterType


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('dcim-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class RegionTest(APIViewTestCases.APIViewTestCase):
    model = Region
    brief_fields = ['id', 'name', 'site_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Region 4',
            'slug': 'region-4',
        },
        {
            'name': 'Region 5',
            'slug': 'region-5',
        },
        {
            'name': 'Region 6',
            'slug': 'region-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        Region.objects.create(name='Region 1', slug='region-1')
        Region.objects.create(name='Region 2', slug='region-2')
        Region.objects.create(name='Region 3', slug='region-3')


class SiteTest(APIViewTestCases.APIViewTestCase):
    model = Site
    brief_fields = ['id', 'name', 'slug', 'url']

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name='Test Region 1', slug='test-region-1'),
            Region.objects.create(name='Test Region 2', slug='test-region-2'),
        )

        sites = (
            Site(region=regions[0], name='Site 1', slug='site-1'),
            Site(region=regions[0], name='Site 2', slug='site-2'),
            Site(region=regions[0], name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        cls.create_data = [
            {
                'name': 'Site 4',
                'slug': 'site-4',
                'region': regions[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
            },
            {
                'name': 'Site 5',
                'slug': 'site-5',
                'region': regions[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
            },
            {
                'name': 'Site 6',
                'slug': 'site-6',
                'region': regions[1].pk,
                'status': SiteStatusChoices.STATUS_ACTIVE,
            },
        ]

    def test_get_site_graphs(self):
        """
        Test retrieval of Graphs assigned to Sites.
        """
        ct = ContentType.objects.get_for_model(Site)
        graphs = (
            Graph(type=ct, name='Graph 1', source='http://example.com/graphs.py?site={{ obj.slug }}&foo=1'),
            Graph(type=ct, name='Graph 2', source='http://example.com/graphs.py?site={{ obj.slug }}&foo=2'),
            Graph(type=ct, name='Graph 3', source='http://example.com/graphs.py?site={{ obj.slug }}&foo=3'),
        )
        Graph.objects.bulk_create(graphs)

        self.add_permissions('dcim.view_site')
        url = reverse('dcim-api:site-graphs', kwargs={'pk': Site.objects.unrestricted().first().pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?site=site-1&foo=1')


class RackGroupTest(APIViewTestCases.APIViewTestCase):
    model = RackGroup
    brief_fields = ['id', 'name', 'rack_count', 'slug', 'url']

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        parent_rack_groups = (
            RackGroup.objects.create(site=sites[0], name='Parent Rack Group 1', slug='parent-rack-group-1'),
            RackGroup.objects.create(site=sites[1], name='Parent Rack Group 2', slug='parent-rack-group-2'),
        )

        RackGroup.objects.create(site=sites[0], name='Rack Group 1', slug='rack-group-1', parent=parent_rack_groups[0])
        RackGroup.objects.create(site=sites[0], name='Rack Group 2', slug='rack-group-2', parent=parent_rack_groups[0])
        RackGroup.objects.create(site=sites[0], name='Rack Group 3', slug='rack-group-3', parent=parent_rack_groups[0])

        cls.create_data = [
            {
                'name': 'Test Rack Group 4',
                'slug': 'test-rack-group-4',
                'site': sites[1].pk,
                'parent': parent_rack_groups[1].pk,
            },
            {
                'name': 'Test Rack Group 5',
                'slug': 'test-rack-group-5',
                'site': sites[1].pk,
                'parent': parent_rack_groups[1].pk,
            },
            {
                'name': 'Test Rack Group 6',
                'slug': 'test-rack-group-6',
                'site': sites[1].pk,
                'parent': parent_rack_groups[1].pk,
            },
        ]


class RackRoleTest(APIViewTestCases.APIViewTestCase):
    model = RackRole
    brief_fields = ['id', 'name', 'rack_count', 'slug', 'url']
    create_data = [
        {
            'name': 'Rack Role 4',
            'slug': 'rack-role-4',
            'color': 'ffff00',
        },
        {
            'name': 'Rack Role 5',
            'slug': 'rack-role-5',
            'color': 'ffff00',
        },
        {
            'name': 'Rack Role 6',
            'slug': 'rack-role-6',
            'color': 'ffff00',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
            RackRole(name='Rack Role 3', slug='rack-role-3', color='0000ff'),
        )
        RackRole.objects.bulk_create(rack_roles)


class RackTest(APIViewTestCases.APIViewTestCase):
    model = Rack
    brief_fields = ['device_count', 'display_name', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup.objects.create(site=sites[0], name='Rack Group 1', slug='rack-group-1'),
            RackGroup.objects.create(site=sites[1], name='Rack Group 2', slug='rack-group-2'),
        )

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
        )
        RackRole.objects.bulk_create(rack_roles)

        racks = (
            Rack(site=sites[0], group=rack_groups[0], role=rack_roles[0], name='Rack 1'),
            Rack(site=sites[0], group=rack_groups[0], role=rack_roles[0], name='Rack 2'),
            Rack(site=sites[0], group=rack_groups[0], role=rack_roles[0], name='Rack 3'),
        )
        Rack.objects.bulk_create(racks)

        cls.create_data = [
            {
                'name': 'Test Rack 4',
                'site': sites[1].pk,
                'group': rack_groups[1].pk,
                'role': rack_roles[1].pk,
            },
            {
                'name': 'Test Rack 5',
                'site': sites[1].pk,
                'group': rack_groups[1].pk,
                'role': rack_roles[1].pk,
            },
            {
                'name': 'Test Rack 6',
                'site': sites[1].pk,
                'group': rack_groups[1].pk,
                'role': rack_roles[1].pk,
            },
        ]

    def test_get_rack_elevation(self):
        """
        GET a single rack elevation.
        """
        rack = Rack.objects.first()
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-elevation', kwargs={'pk': rack.pk})

        # Retrieve all units
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 42)

        # Search for specific units
        response = self.client.get(f'{url}?q=3', **self.header)
        self.assertEqual(response.data['count'], 13)
        response = self.client.get(f'{url}?q=U3', **self.header)
        self.assertEqual(response.data['count'], 11)
        response = self.client.get(f'{url}?q=U10', **self.header)
        self.assertEqual(response.data['count'], 1)

    def test_get_rack_elevation_svg(self):
        """
        GET a single rack elevation in SVG format.
        """
        rack = Rack.objects.first()
        self.add_permissions('dcim.view_rack')
        url = '{}?render=svg'.format(reverse('dcim-api:rack-elevation', kwargs={'pk': rack.pk}))

        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'image/svg+xml')


class RackReservationTest(APIViewTestCases.APIViewTestCase):
    model = RackReservation
    brief_fields = ['id', 'units', 'url', 'user']

    @classmethod
    def setUpTestData(cls):

        user = User.objects.create(username='user1', is_active=True)

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')

        cls.racks = (
            Rack(site=site, name='Rack 1'),
            Rack(site=site, name='Rack 2'),
        )
        Rack.objects.bulk_create(cls.racks)

        rack_reservations = (
            RackReservation(rack=cls.racks[0], units=[1, 2, 3], user=user, description='Reservation #1'),
            RackReservation(rack=cls.racks[0], units=[4, 5, 6], user=user, description='Reservation #2'),
            RackReservation(rack=cls.racks[0], units=[7, 8, 9], user=user, description='Reservation #3'),
        )
        RackReservation.objects.bulk_create(rack_reservations)

    def setUp(self):
        super().setUp()

        # We have to set creation data under setUp() because we need access to the test user.
        self.create_data = [
            {
                'rack': self.racks[1].pk,
                'units': [10, 11, 12],
                'user': self.user.pk,
                'description': 'Reservation #4',
            },
            {
                'rack': self.racks[1].pk,
                'units': [13, 14, 15],
                'user': self.user.pk,
                'description': 'Reservation #5',
            },
            {
                'rack': self.racks[1].pk,
                'units': [16, 17, 18],
                'user': self.user.pk,
                'description': 'Reservation #6',
            },
        ]


class ManufacturerTest(APIViewTestCases.APIViewTestCase):
    model = Manufacturer
    brief_fields = ['devicetype_count', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Manufacturer 4',
            'slug': 'manufacturer-4',
        },
        {
            'name': 'Manufacturer 5',
            'slug': 'manufacturer-5',
        },
        {
            'name': 'Manufacturer 6',
            'slug': 'manufacturer-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)


class DeviceTypeTest(APIViewTestCases.APIViewTestCase):
    model = DeviceType
    brief_fields = ['device_count', 'display_name', 'id', 'manufacturer', 'model', 'slug', 'url']

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        cls.create_data = [
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 4',
                'slug': 'device-type-4',
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 5',
                'slug': 'device-type-5',
            },
            {
                'manufacturer': manufacturers[1].pk,
                'model': 'Device Type 6',
                'slug': 'device-type-6',
            },
        ]


class ConsolePortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ConsolePortTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        console_port_templates = (
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 1'),
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 2'),
            ConsolePortTemplate(device_type=devicetype, name='Console Port Template 3'),
        )
        ConsolePortTemplate.objects.bulk_create(console_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Console Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Port Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Port Template 6',
            },
        ]


class ConsoleServerPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ConsoleServerPortTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        console_server_port_templates = (
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 1'),
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 2'),
            ConsoleServerPortTemplate(device_type=devicetype, name='Console Server Port Template 3'),
        )
        ConsoleServerPortTemplate.objects.bulk_create(console_server_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Console Server Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Server Port Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Console Server Port Template 6',
            },
        ]


class PowerPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = PowerPortTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        power_port_templates = (
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 1'),
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 2'),
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 3'),
        )
        PowerPortTemplate.objects.bulk_create(power_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Power Port Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Port Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Port Template 6',
            },
        ]


class PowerOutletTemplateTest(APIViewTestCases.APIViewTestCase):
    model = PowerOutletTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        power_outlet_templates = (
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 1'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 2'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 3'),
        )
        PowerOutletTemplate.objects.bulk_create(power_outlet_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Power Outlet Template 6',
            },
        ]


class InterfaceTemplateTest(APIViewTestCases.APIViewTestCase):
    model = InterfaceTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        interface_templates = (
            InterfaceTemplate(device_type=devicetype, name='Interface Template 1', type='1000base-t'),
            InterfaceTemplate(device_type=devicetype, name='Interface Template 2', type='1000base-t'),
            InterfaceTemplate(device_type=devicetype, name='Interface Template 3', type='1000base-t'),
        )
        InterfaceTemplate.objects.bulk_create(interface_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Interface Template 4',
                'type': '1000base-t',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Interface Template 5',
                'type': '1000base-t',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Interface Template 6',
                'type': '1000base-t',
            },
        ]


class FrontPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = FrontPortTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        rear_port_templates = (
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 2', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 3', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 4', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 5', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 6', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_port_templates)

        front_port_templates = (
            FrontPortTemplate(
                device_type=devicetype,
                name='Front Port Template 1',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[0]
            ),
            FrontPortTemplate(
                device_type=devicetype,
                name='Front Port Template 2',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[1]
            ),
            FrontPortTemplate(
                device_type=devicetype,
                name='Front Port Template 3',
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_port_templates[2]
            ),
        )
        FrontPortTemplate.objects.bulk_create(front_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Front Port Template 4',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[3].pk,
                'position': 1,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Front Port Template 5',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[4].pk,
                'position': 1,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Front Port Template 6',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_port_templates[5].pk,
                'position': 1,
            },
        ]


class RearPortTemplateTest(APIViewTestCases.APIViewTestCase):
    model = RearPortTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        rear_port_templates = (
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 2', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 3', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_port_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Rear Port Template 4',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Rear Port Template 5',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device_type': devicetype.pk,
                'name': 'Rear Port Template 6',
                'type': PortTypeChoices.TYPE_8P8C,
            },
        ]


class DeviceBayTemplateTest(APIViewTestCases.APIViewTestCase):
    model = DeviceBayTemplate
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        device_bay_templates = (
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 1'),
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 2'),
            DeviceBayTemplate(device_type=devicetype, name='Device Bay Template 3'),
        )
        DeviceBayTemplate.objects.bulk_create(device_bay_templates)

        cls.create_data = [
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 4',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 5',
            },
            {
                'device_type': devicetype.pk,
                'name': 'Device Bay Template 6',
            },
        ]


class DeviceRoleTest(APIViewTestCases.APIViewTestCase):
    model = DeviceRole
    brief_fields = ['device_count', 'id', 'name', 'slug', 'url', 'virtualmachine_count']
    create_data = [
        {
            'name': 'Device Role 4',
            'slug': 'device-role-4',
            'color': 'ffff00',
        },
        {
            'name': 'Device Role 5',
            'slug': 'device-role-5',
            'color': 'ffff00',
        },
        {
            'name': 'Device Role 6',
            'slug': 'device-role-6',
            'color': 'ffff00',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        device_roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1', color='ff0000'),
            DeviceRole(name='Device Role 2', slug='device-role-2', color='00ff00'),
            DeviceRole(name='Device Role 3', slug='device-role-3', color='0000ff'),
        )
        DeviceRole.objects.bulk_create(device_roles)


class PlatformTest(APIViewTestCases.APIViewTestCase):
    model = Platform
    brief_fields = ['device_count', 'id', 'name', 'slug', 'url', 'virtualmachine_count']
    create_data = [
        {
            'name': 'Platform 4',
            'slug': 'platform-4',
        },
        {
            'name': 'Platform 5',
            'slug': 'platform-5',
        },
        {
            'name': 'Platform 6',
            'slug': 'platform-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)


class DeviceTest(APIViewTestCases.APIViewTestCase):
    model = Device
    brief_fields = ['display_name', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(device_types)

        device_roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1', color='ff0000'),
            DeviceRole(name='Device Role 2', slug='device-role-2', color='00ff00'),
        )
        DeviceRole.objects.bulk_create(device_roles)

        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        clusters = (
            Cluster(name='Cluster 1', type=cluster_type),
            Cluster(name='Cluster 2', type=cluster_type),
        )
        Cluster.objects.bulk_create(clusters)

        devices = (
            Device(
                device_type=device_types[0],
                device_role=device_roles[0],
                name='Device 1',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'A': 1}
            ),
            Device(
                device_type=device_types[0],
                device_role=device_roles[0],
                name='Device 2',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'B': 2}
            ),
            Device(
                device_type=device_types[0],
                device_role=device_roles[0],
                name='Device 3',
                site=sites[0],
                rack=racks[0],
                cluster=clusters[0],
                local_context_data={'C': 3}
            ),
        )
        Device.objects.bulk_create(devices)

        cls.create_data = [
            {
                'device_type': device_types[1].pk,
                'device_role': device_roles[1].pk,
                'name': 'Test Device 4',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
            {
                'device_type': device_types[1].pk,
                'device_role': device_roles[1].pk,
                'name': 'Test Device 5',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
            {
                'device_type': device_types[1].pk,
                'device_role': device_roles[1].pk,
                'name': 'Test Device 6',
                'site': sites[1].pk,
                'rack': racks[1].pk,
                'cluster': clusters[1].pk,
            },
        ]

    def test_get_device_graphs(self):
        """
        Test retrieval of Graphs assigned to Devices.
        """
        ct = ContentType.objects.get_for_model(Device)
        graphs = (
            Graph(type=ct, name='Graph 1', source='http://example.com/graphs.py?device={{ obj.name }}&foo=1'),
            Graph(type=ct, name='Graph 2', source='http://example.com/graphs.py?device={{ obj.name }}&foo=2'),
            Graph(type=ct, name='Graph 3', source='http://example.com/graphs.py?device={{ obj.name }}&foo=3'),
        )
        Graph.objects.bulk_create(graphs)

        self.add_permissions('dcim.view_device')
        url = reverse('dcim-api:device-graphs', kwargs={'pk': Device.objects.unrestricted().first().pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?device=Device 1&foo=1')

    def test_config_context_included_by_default_in_list_view(self):
        """
        Check that config context data is included by default in the devices list.
        """
        self.add_permissions('dcim.view_device')
        url = reverse('dcim-api:device-list') + '?slug=device-with-context-data'
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['results'][0].get('config_context', {}).get('A'), 1)

    def test_config_context_excluded(self):
        """
        Check that config context data can be excluded by passing ?exclude=config_context.
        """
        self.add_permissions('dcim.view_device')
        url = reverse('dcim-api:device-list') + '?exclude=config_context'
        response = self.client.get(url, **self.header)

        self.assertFalse('config_context' in response.data['results'][0])

    def test_unique_name_per_site_constraint(self):
        """
        Check that creating a device with a duplicate name within a site fails.
        """
        device = Device.objects.first()
        data = {
            'device_type': device.device_type.pk,
            'device_role': device.device_role.pk,
            'site': device.site.pk,
            'name': device.name,
        }

        self.add_permissions('dcim.add_device')
        url = reverse('dcim-api:device-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


class ConsolePortTest(APIViewTestCases.APIViewTestCase):
    model = ConsolePort
    brief_fields = ['cable', 'connection_status', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        console_ports = (
            ConsolePort(device=device, name='Console Port 1'),
            ConsolePort(device=device, name='Console Port 2'),
            ConsolePort(device=device, name='Console Port 3'),
        )
        ConsolePort.objects.bulk_create(console_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Console Port 4',
            },
            {
                'device': device.pk,
                'name': 'Console Port 5',
            },
            {
                'device': device.pk,
                'name': 'Console Port 6',
            },
        ]

    def test_trace_consoleport(self):
        """
        Test tracing a ConsolePort cable.
        """
        consoleport = ConsolePort.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        consoleserverport = ConsoleServerPort.objects.create(
            device=peer_device,
            name='Console Server Port 1'
        )
        cable = Cable(termination_a=consoleport, termination_b=consoleserverport, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_consoleport')
        url = reverse('dcim-api:consoleport-trace', kwargs={'pk': consoleport.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], consoleport.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], consoleserverport.name)


class ConsoleServerPortTest(APIViewTestCases.APIViewTestCase):
    model = ConsoleServerPort
    brief_fields = ['cable', 'connection_status', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        console_server_ports = (
            ConsoleServerPort(device=device, name='Console Server Port 1'),
            ConsoleServerPort(device=device, name='Console Server Port 2'),
            ConsoleServerPort(device=device, name='Console Server Port 3'),
        )
        ConsoleServerPort.objects.bulk_create(console_server_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Console Server Port 4',
            },
            {
                'device': device.pk,
                'name': 'Console Server Port 5',
            },
            {
                'device': device.pk,
                'name': 'Console Server Port 6',
            },
        ]

    def test_trace_consoleserverport(self):
        """
        Test tracing a ConsoleServerPort cable.
        """
        consoleserverport = ConsoleServerPort.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        consoleport = ConsolePort.objects.create(
            device=peer_device,
            name='Console Port 1'
        )
        cable = Cable(termination_a=consoleserverport, termination_b=consoleport, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_consoleserverport')
        url = reverse('dcim-api:consoleserverport-trace', kwargs={'pk': consoleserverport.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], consoleserverport.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], consoleport.name)


class PowerPortTest(APIViewTestCases.APIViewTestCase):
    model = PowerPort
    brief_fields = ['cable', 'connection_status', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        power_ports = (
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
            PowerPort(device=device, name='Power Port 3'),
        )
        PowerPort.objects.bulk_create(power_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Power Port 4',
            },
            {
                'device': device.pk,
                'name': 'Power Port 5',
            },
            {
                'device': device.pk,
                'name': 'Power Port 6',
            },
        ]

    def test_trace_powerport(self):
        """
        Test tracing a PowerPort cable.
        """
        powerport = PowerPort.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        poweroutlet = PowerOutlet.objects.create(
            device=peer_device,
            name='Power Outlet 1'
        )
        cable = Cable(termination_a=powerport, termination_b=poweroutlet, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_powerport')
        url = reverse('dcim-api:powerport-trace', kwargs={'pk': powerport.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], powerport.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], poweroutlet.name)


class PowerOutletTest(APIViewTestCases.APIViewTestCase):
    model = PowerOutlet
    brief_fields = ['cable', 'connection_status', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        power_outlets = (
            PowerOutlet(device=device, name='Power Outlet 1'),
            PowerOutlet(device=device, name='Power Outlet 2'),
            PowerOutlet(device=device, name='Power Outlet 3'),
        )
        PowerOutlet.objects.bulk_create(power_outlets)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Power Outlet 4',
            },
            {
                'device': device.pk,
                'name': 'Power Outlet 5',
            },
            {
                'device': device.pk,
                'name': 'Power Outlet 6',
            },
        ]

    def test_trace_poweroutlet(self):
        """
        Test tracing a PowerOutlet cable.
        """
        poweroutlet = PowerOutlet.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        powerport = PowerPort.objects.create(
            device=peer_device,
            name='Power Port 1'
        )
        cable = Cable(termination_a=poweroutlet, termination_b=powerport, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_poweroutlet')
        url = reverse('dcim-api:poweroutlet-trace', kwargs={'pk': poweroutlet.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], poweroutlet.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], powerport.name)


class InterfaceTest(APIViewTestCases.APIViewTestCase):
    model = Interface
    brief_fields = ['cable', 'connection_status', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        interfaces = (
            Interface(device=device, name='Interface 1', type='1000base-t'),
            Interface(device=device, name='Interface 2', type='1000base-t'),
            Interface(device=device, name='Interface 3', type='1000base-t'),
        )
        Interface.objects.bulk_create(interfaces)

        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Interface 4',
                'type': '1000base-t',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'device': device.pk,
                'name': 'Interface 5',
                'type': '1000base-t',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'device': device.pk,
                'name': 'Interface 6',
                'type': '1000base-t',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
        ]

    def test_get_interface_graphs(self):
        """
        Test retrieval of Graphs assigned to Devices.
        """
        ct = ContentType.objects.get_for_model(Interface)
        graphs = (
            Graph(type=ct, name='Graph 1', source='http://example.com/graphs.py?interface={{ obj.name }}&foo=1'),
            Graph(type=ct, name='Graph 2', source='http://example.com/graphs.py?interface={{ obj.name }}&foo=2'),
            Graph(type=ct, name='Graph 3', source='http://example.com/graphs.py?interface={{ obj.name }}&foo=3'),
        )
        Graph.objects.bulk_create(graphs)

        self.add_permissions('dcim.view_interface')
        url = reverse('dcim-api:interface-graphs', kwargs={'pk': Interface.objects.unrestricted().first().pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?interface=Interface 1&foo=1')

    def test_trace_interface(self):
        """
        Test tracing an Interface cable.
        """
        interface_a = Interface.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        interface_b = Interface.objects.create(
            device=peer_device,
            name='Interface X'
        )
        cable = Cable(termination_a=interface_a, termination_b=interface_b, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_interface')
        url = reverse('dcim-api:interface-trace', kwargs={'pk': interface_a.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], interface_a.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], interface_b.name)


class FrontPortTest(APIViewTestCases.APIViewTestCase):
    model = FrontPort
    brief_fields = ['cable', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        rear_ports = (
            RearPort(device=device, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 4', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 5', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 6', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(rear_ports)

        front_ports = (
            FrontPort(device=device, name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPort(device=device, name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[1]),
            FrontPort(device=device, name='Front Port 3', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[2]),
        )
        FrontPort.objects.bulk_create(front_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Front Port 4',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[3].pk,
                'rear_port_position': 1,
            },
            {
                'device': device.pk,
                'name': 'Front Port 5',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[4].pk,
                'rear_port_position': 1,
            },
            {
                'device': device.pk,
                'name': 'Front Port 6',
                'type': PortTypeChoices.TYPE_8P8C,
                'rear_port': rear_ports[5].pk,
                'rear_port_position': 1,
            },
        ]

    def test_trace_frontport(self):
        """
        Test tracing a FrontPort cable.
        """
        frontport = FrontPort.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        interface = Interface.objects.create(
            device=peer_device,
            name='Interface X'
        )
        cable = Cable(termination_a=frontport, termination_b=interface, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_frontport')
        url = reverse('dcim-api:frontport-trace', kwargs={'pk': frontport.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], frontport.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], interface.name)


class RearPortTest(APIViewTestCases.APIViewTestCase):
    model = RearPort
    brief_fields = ['cable', 'device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        rear_ports = (
            RearPort(device=device, name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=device, name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(rear_ports)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Rear Port 4',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device': device.pk,
                'name': 'Rear Port 5',
                'type': PortTypeChoices.TYPE_8P8C,
            },
            {
                'device': device.pk,
                'name': 'Rear Port 6',
                'type': PortTypeChoices.TYPE_8P8C,
            },
        ]

    def test_trace_rearport(self):
        """
        Test tracing a RearPort cable.
        """
        rearport = RearPort.objects.first()
        peer_device = Device.objects.create(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            device_role=DeviceRole.objects.first(),
            name='Peer Device'
        )
        interface = Interface.objects.create(
            device=peer_device,
            name='Interface X'
        )
        cable = Cable(termination_a=rearport, termination_b=interface, label='Cable 1')
        cable.save()

        self.add_permissions('dcim.view_rearport')
        url = reverse('dcim-api:rearport-trace', kwargs={'pk': rearport.pk})
        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        segment1 = response.data[0]
        self.assertEqual(segment1[0]['name'], rearport.name)
        self.assertEqual(segment1[1]['label'], cable.label)
        self.assertEqual(segment1[2]['name'], interface.name)


class DeviceBayTest(APIViewTestCases.APIViewTestCase):
    model = DeviceBay
    brief_fields = ['device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')

        device_types = (
            DeviceType(
                manufacturer=manufacturer,
                model='Device Type 1',
                slug='device-type-1',
                subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
            ),
            DeviceType(
                manufacturer=manufacturer,
                model='Device Type 2',
                slug='device-type-2',
                subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
            ),
        )
        DeviceType.objects.bulk_create(device_types)

        devices = (
            Device(device_type=device_types[0], device_role=devicerole, name='Device 1', site=site),
            Device(device_type=device_types[1], device_role=devicerole, name='Device 2', site=site),
            Device(device_type=device_types[1], device_role=devicerole, name='Device 3', site=site),
            Device(device_type=device_types[1], device_role=devicerole, name='Device 4', site=site),
        )
        Device.objects.bulk_create(devices)

        device_bays = (
            DeviceBay(device=devices[0], name='Device Bay 1'),
            DeviceBay(device=devices[0], name='Device Bay 2'),
            DeviceBay(device=devices[0], name='Device Bay 3'),
        )
        DeviceBay.objects.bulk_create(device_bays)

        cls.create_data = [
            {
                'device': devices[0].pk,
                'name': 'Device Bay 4',
                'installed_device': devices[1].pk,
            },
            {
                'device': devices[0].pk,
                'name': 'Device Bay 5',
                'installed_device': devices[2].pk,
            },
            {
                'device': devices[0].pk,
                'name': 'Device Bay 6',
                'installed_device': devices[3].pk,
            },
        ]


class InventoryItemTest(APIViewTestCases.APIViewTestCase):
    model = InventoryItem
    brief_fields = ['device', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1', color='ff0000')
        device = Device.objects.create(device_type=devicetype, device_role=devicerole, name='Device 1', site=site)

        inventory_items = (
            InventoryItem(device=device, name='Inventory Item 1', manufacturer=manufacturer),
            InventoryItem(device=device, name='Inventory Item 2', manufacturer=manufacturer),
            InventoryItem(device=device, name='Inventory Item 3', manufacturer=manufacturer),
        )
        InventoryItem.objects.bulk_create(inventory_items)

        cls.create_data = [
            {
                'device': device.pk,
                'name': 'Inventory Item 4',
                'manufacturer': manufacturer.pk,
            },
            {
                'device': device.pk,
                'name': 'Inventory Item 5',
                'manufacturer': manufacturer.pk,
            },
            {
                'device': device.pk,
                'name': 'Inventory Item 6',
                'manufacturer': manufacturer.pk,
            },
        ]


class CableTest(APIViewTestCases.APIViewTestCase):
    model = Cable
    brief_fields = ['id', 'label', 'url']

    # TODO: Allow updating cable terminations
    test_update_object = None

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1', color='ff0000')

        devices = (
            Device(device_type=devicetype, device_role=devicerole, name='Device 1', site=site),
            Device(device_type=devicetype, device_role=devicerole, name='Device 2', site=site),
        )
        Device.objects.bulk_create(devices)

        interfaces = []
        for device in devices:
            for i in range(0, 10):
                interfaces.append(Interface(device=device, type=InterfaceTypeChoices.TYPE_1GE_FIXED, name=f'eth{i}'))
        Interface.objects.bulk_create(interfaces)

        cables = (
            Cable(termination_a=interfaces[0], termination_b=interfaces[10], label='Cable 1'),
            Cable(termination_a=interfaces[1], termination_b=interfaces[11], label='Cable 2'),
            Cable(termination_a=interfaces[2], termination_b=interfaces[12], label='Cable 3'),
        )
        for cable in cables:
            cable.save()

        cls.create_data = [
            {
                'termination_a_type': 'dcim.interface',
                'termination_a_id': interfaces[4].pk,
                'termination_b_type': 'dcim.interface',
                'termination_b_id': interfaces[14].pk,
                'label': 'Cable 4',
            },
            {
                'termination_a_type': 'dcim.interface',
                'termination_a_id': interfaces[5].pk,
                'termination_b_type': 'dcim.interface',
                'termination_b_id': interfaces[15].pk,
                'label': 'Cable 5',
            },
            {
                'termination_a_type': 'dcim.interface',
                'termination_a_id': interfaces[6].pk,
                'termination_b_type': 'dcim.interface',
                'termination_b_id': interfaces[16].pk,
                'label': 'Cable 6',
            },
        ]


class ConnectionTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.site = Site.objects.create(
            name='Test Site 1', slug='test-site-1'
        )
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer 1', slug='test-manufacturer-1'
        )
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=self.site
        )
        self.device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 2', site=self.site
        )
        self.panel1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Panel 1', site=self.site
        )
        self.panel2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Panel 2', site=self.site
        )

    def test_create_direct_console_connection(self):

        consoleport1 = ConsolePort.objects.create(
            device=self.device1, name='Test Console Port 1'
        )
        consoleserverport1 = ConsoleServerPort.objects.create(
            device=self.device2, name='Test Console Server Port 1'
        )

        data = {
            'termination_a_type': 'dcim.consoleport',
            'termination_a_id': consoleport1.pk,
            'termination_b_type': 'dcim.consoleserverport',
            'termination_b_id': consoleserverport1.pk,
        }

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cable.objects.count(), 1)

        cable = Cable.objects.get(pk=response.data['id'])
        consoleport1 = ConsolePort.objects.get(pk=consoleport1.pk)
        consoleserverport1 = ConsoleServerPort.objects.get(pk=consoleserverport1.pk)

        self.assertEqual(cable.termination_a, consoleport1)
        self.assertEqual(cable.termination_b, consoleserverport1)
        self.assertEqual(consoleport1.cable, cable)
        self.assertEqual(consoleserverport1.cable, cable)
        self.assertEqual(consoleport1.connected_endpoint, consoleserverport1)
        self.assertEqual(consoleserverport1.connected_endpoint, consoleport1)

    def test_create_patched_console_connection(self):

        consoleport1 = ConsolePort.objects.create(
            device=self.device1, name='Test Console Port 1'
        )
        consoleserverport1 = ConsoleServerPort.objects.create(
            device=self.device2, name='Test Console Server Port 1'
        )
        rearport1 = RearPort.objects.create(
            device=self.panel1, name='Test Rear Port 1', type=PortTypeChoices.TYPE_8P8C
        )
        frontport1 = FrontPort.objects.create(
            device=self.panel1, name='Test Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport1
        )
        rearport2 = RearPort.objects.create(
            device=self.panel2, name='Test Rear Port 2', type=PortTypeChoices.TYPE_8P8C
        )
        frontport2 = FrontPort.objects.create(
            device=self.panel2, name='Test Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport2
        )

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        cables = [
            # Console port to panel1 front
            {
                'termination_a_type': 'dcim.consoleport',
                'termination_a_id': consoleport1.pk,
                'termination_b_type': 'dcim.frontport',
                'termination_b_id': frontport1.pk,
            },
            # Panel1 rear to panel2 rear
            {
                'termination_a_type': 'dcim.rearport',
                'termination_a_id': rearport1.pk,
                'termination_b_type': 'dcim.rearport',
                'termination_b_id': rearport2.pk,
            },
            # Panel2 front to console server port
            {
                'termination_a_type': 'dcim.frontport',
                'termination_a_id': frontport2.pk,
                'termination_b_type': 'dcim.consoleserverport',
                'termination_b_id': consoleserverport1.pk,
            },
        ]

        for data in cables:

            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)

            cable = Cable.objects.get(pk=response.data['id'])
            self.assertEqual(cable.termination_a.cable, cable)
            self.assertEqual(cable.termination_b.cable, cable)

        consoleport1 = ConsolePort.objects.get(pk=consoleport1.pk)
        consoleserverport1 = ConsoleServerPort.objects.get(pk=consoleserverport1.pk)
        self.assertEqual(consoleport1.connected_endpoint, consoleserverport1)
        self.assertEqual(consoleserverport1.connected_endpoint, consoleport1)

    def test_create_direct_power_connection(self):

        powerport1 = PowerPort.objects.create(
            device=self.device1, name='Test Power Port 1'
        )
        poweroutlet1 = PowerOutlet.objects.create(
            device=self.device2, name='Test Power Outlet 1'
        )

        data = {
            'termination_a_type': 'dcim.powerport',
            'termination_a_id': powerport1.pk,
            'termination_b_type': 'dcim.poweroutlet',
            'termination_b_id': poweroutlet1.pk,
        }

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cable.objects.count(), 1)

        cable = Cable.objects.get(pk=response.data['id'])
        powerport1 = PowerPort.objects.get(pk=powerport1.pk)
        poweroutlet1 = PowerOutlet.objects.get(pk=poweroutlet1.pk)

        self.assertEqual(cable.termination_a, powerport1)
        self.assertEqual(cable.termination_b, poweroutlet1)
        self.assertEqual(powerport1.cable, cable)
        self.assertEqual(poweroutlet1.cable, cable)
        self.assertEqual(powerport1.connected_endpoint, poweroutlet1)
        self.assertEqual(poweroutlet1.connected_endpoint, powerport1)

    # Note: Power connections via patch ports are not supported.

    def test_create_direct_interface_connection(self):

        interface1 = Interface.objects.create(
            device=self.device1, name='Test Interface 1'
        )
        interface2 = Interface.objects.create(
            device=self.device2, name='Test Interface 2'
        )

        data = {
            'termination_a_type': 'dcim.interface',
            'termination_a_id': interface1.pk,
            'termination_b_type': 'dcim.interface',
            'termination_b_id': interface2.pk,
        }

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cable.objects.count(), 1)

        cable = Cable.objects.get(pk=response.data['id'])
        interface1 = Interface.objects.get(pk=interface1.pk)
        interface2 = Interface.objects.get(pk=interface2.pk)

        self.assertEqual(cable.termination_a, interface1)
        self.assertEqual(cable.termination_b, interface2)
        self.assertEqual(interface1.cable, cable)
        self.assertEqual(interface2.cable, cable)
        self.assertEqual(interface1.connected_endpoint, interface2)
        self.assertEqual(interface2.connected_endpoint, interface1)

    def test_create_patched_interface_connection(self):

        interface1 = Interface.objects.create(
            device=self.device1, name='Test Interface 1'
        )
        interface2 = Interface.objects.create(
            device=self.device2, name='Test Interface 2'
        )
        rearport1 = RearPort.objects.create(
            device=self.panel1, name='Test Rear Port 1', type=PortTypeChoices.TYPE_8P8C
        )
        frontport1 = FrontPort.objects.create(
            device=self.panel1, name='Test Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport1
        )
        rearport2 = RearPort.objects.create(
            device=self.panel2, name='Test Rear Port 2', type=PortTypeChoices.TYPE_8P8C
        )
        frontport2 = FrontPort.objects.create(
            device=self.panel2, name='Test Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport2
        )

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        cables = [
            # Interface1 to panel1 front
            {
                'termination_a_type': 'dcim.interface',
                'termination_a_id': interface1.pk,
                'termination_b_type': 'dcim.frontport',
                'termination_b_id': frontport1.pk,
            },
            # Panel1 rear to panel2 rear
            {
                'termination_a_type': 'dcim.rearport',
                'termination_a_id': rearport1.pk,
                'termination_b_type': 'dcim.rearport',
                'termination_b_id': rearport2.pk,
            },
            # Panel2 front to interface2
            {
                'termination_a_type': 'dcim.frontport',
                'termination_a_id': frontport2.pk,
                'termination_b_type': 'dcim.interface',
                'termination_b_id': interface2.pk,
            },
        ]

        for data in cables:

            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)

            cable = Cable.objects.get(pk=response.data['id'])
            self.assertEqual(cable.termination_a.cable, cable)
            self.assertEqual(cable.termination_b.cable, cable)

        interface1 = Interface.objects.get(pk=interface1.pk)
        interface2 = Interface.objects.get(pk=interface2.pk)
        self.assertEqual(interface1.connected_endpoint, interface2)
        self.assertEqual(interface2.connected_endpoint, interface1)

    def test_create_direct_circuittermination_connection(self):

        provider = Provider.objects.create(
            name='Test Provider 1', slug='test-provider-1'
        )
        circuittype = CircuitType.objects.create(
            name='Test Circuit Type 1', slug='test-circuit-type-1'
        )
        circuit = Circuit.objects.create(
            provider=provider, type=circuittype, cid='Test Circuit 1'
        )
        interface1 = Interface.objects.create(
            device=self.device1, name='Test Interface 1'
        )
        circuittermination1 = CircuitTermination.objects.create(
            circuit=circuit, term_side='A', site=self.site, port_speed=10000
        )

        data = {
            'termination_a_type': 'dcim.interface',
            'termination_a_id': interface1.pk,
            'termination_b_type': 'circuits.circuittermination',
            'termination_b_id': circuittermination1.pk,
        }

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cable.objects.count(), 1)

        cable = Cable.objects.get(pk=response.data['id'])
        interface1 = Interface.objects.get(pk=interface1.pk)
        circuittermination1 = CircuitTermination.objects.get(pk=circuittermination1.pk)

        self.assertEqual(cable.termination_a, interface1)
        self.assertEqual(cable.termination_b, circuittermination1)
        self.assertEqual(interface1.cable, cable)
        self.assertEqual(circuittermination1.cable, cable)
        self.assertEqual(interface1.connected_endpoint, circuittermination1)
        self.assertEqual(circuittermination1.connected_endpoint, interface1)

    def test_create_patched_circuittermination_connection(self):

        provider = Provider.objects.create(
            name='Test Provider 1', slug='test-provider-1'
        )
        circuittype = CircuitType.objects.create(
            name='Test Circuit Type 1', slug='test-circuit-type-1'
        )
        circuit = Circuit.objects.create(
            provider=provider, type=circuittype, cid='Test Circuit 1'
        )
        interface1 = Interface.objects.create(
            device=self.device1, name='Test Interface 1'
        )
        circuittermination1 = CircuitTermination.objects.create(
            circuit=circuit, term_side='A', site=self.site, port_speed=10000
        )
        rearport1 = RearPort.objects.create(
            device=self.panel1, name='Test Rear Port 1', type=PortTypeChoices.TYPE_8P8C
        )
        frontport1 = FrontPort.objects.create(
            device=self.panel1, name='Test Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport1
        )
        rearport2 = RearPort.objects.create(
            device=self.panel2, name='Test Rear Port 2', type=PortTypeChoices.TYPE_8P8C
        )
        frontport2 = FrontPort.objects.create(
            device=self.panel2, name='Test Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rearport2
        )

        self.add_permissions('dcim.add_cable')
        url = reverse('dcim-api:cable-list')
        cables = [
            # Interface to panel1 front
            {
                'termination_a_type': 'dcim.interface',
                'termination_a_id': interface1.pk,
                'termination_b_type': 'dcim.frontport',
                'termination_b_id': frontport1.pk,
            },
            # Panel1 rear to panel2 rear
            {
                'termination_a_type': 'dcim.rearport',
                'termination_a_id': rearport1.pk,
                'termination_b_type': 'dcim.rearport',
                'termination_b_id': rearport2.pk,
            },
            # Panel2 front to circuit termination
            {
                'termination_a_type': 'dcim.frontport',
                'termination_a_id': frontport2.pk,
                'termination_b_type': 'circuits.circuittermination',
                'termination_b_id': circuittermination1.pk,
            },
        ]

        for data in cables:

            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)

            cable = Cable.objects.get(pk=response.data['id'])
            self.assertEqual(cable.termination_a.cable, cable)
            self.assertEqual(cable.termination_b.cable, cable)

        interface1 = Interface.objects.get(pk=interface1.pk)
        circuittermination1 = CircuitTermination.objects.get(pk=circuittermination1.pk)
        self.assertEqual(interface1.connected_endpoint, circuittermination1)
        self.assertEqual(circuittermination1.connected_endpoint, interface1)


class ConnectedDeviceTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype1 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.devicetype2 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 2', slug='test-device-type-2'
        )
        self.devicerole1 = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.devicerole2 = DeviceRole.objects.create(
            name='Test Device Role 2', slug='test-device-role-2', color='00ff00'
        )
        self.device1 = Device.objects.create(
            device_type=self.devicetype1, device_role=self.devicerole1, name='TestDevice1', site=self.site1
        )
        self.device2 = Device.objects.create(
            device_type=self.devicetype1, device_role=self.devicerole1, name='TestDevice2', site=self.site1
        )
        self.interface1 = Interface.objects.create(device=self.device1, name='eth0')
        self.interface2 = Interface.objects.create(device=self.device2, name='eth0')

        cable = Cable(termination_a=self.interface1, termination_b=self.interface2)
        cable.save()

    def test_get_connected_device(self):

        url = reverse('dcim-api:connected-device-list')
        response = self.client.get(url + '?peer_device=TestDevice2&peer_interface=eth0', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.device1.name)


class VirtualChassisTest(APIViewTestCases.APIViewTestCase):
    model = VirtualChassis
    brief_fields = ['id', 'master', 'member_count', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type', slug='device-type')
        devicerole = DeviceRole.objects.create(name='Device Role', slug='device-role', color='ff0000')

        devices = (
            Device(name='Device 1', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 2', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 3', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 4', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 5', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 6', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 7', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 8', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 9', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 10', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 11', device_type=devicetype, device_role=devicerole, site=site),
            Device(name='Device 12', device_type=devicetype, device_role=devicerole, site=site),
        )
        Device.objects.bulk_create(devices)

        # Create 12 interfaces per device
        interfaces = []
        for i, device in enumerate(devices):
            for j in range(0, 13):
                interfaces.append(
                    # Interface name starts with parent device's position in VC; e.g. 1/1, 1/2, 1/3...
                    Interface(device=device, name=f'{i%3+1}/{j}', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
                )
        Interface.objects.bulk_create(interfaces)

        # Create three VirtualChassis with three members each
        virtual_chassis = (
            VirtualChassis(name='Virtual Chassis 1', master=devices[0], domain='domain-1'),
            VirtualChassis(name='Virtual Chassis 2', master=devices[3], domain='domain-2'),
            VirtualChassis(name='Virtual Chassis 3', master=devices[6], domain='domain-3'),
        )
        VirtualChassis.objects.bulk_create(virtual_chassis)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis[0], vc_position=2)
        Device.objects.filter(pk=devices[2].pk).update(virtual_chassis=virtual_chassis[0], vc_position=3)
        Device.objects.filter(pk=devices[4].pk).update(virtual_chassis=virtual_chassis[1], vc_position=2)
        Device.objects.filter(pk=devices[5].pk).update(virtual_chassis=virtual_chassis[1], vc_position=3)
        Device.objects.filter(pk=devices[7].pk).update(virtual_chassis=virtual_chassis[2], vc_position=2)
        Device.objects.filter(pk=devices[8].pk).update(virtual_chassis=virtual_chassis[2], vc_position=3)

        cls.update_data = {
            'name': 'Virtual Chassis X',
            'domain': 'domain-x',
            'master': devices[1].pk,
        }

        cls.create_data = [
            {
                'name': 'Virtual Chassis 4',
                'domain': 'domain-4',
            },
            {
                'name': 'Virtual Chassis 5',
                'domain': 'domain-5',
            },
            {
                'name': 'Virtual Chassis 6',
                'domain': 'domain-6',
            },
        ]


class PowerPanelTest(APIViewTestCases.APIViewTestCase):
    model = PowerPanel
    brief_fields = ['id', 'name', 'powerfeed_count', 'url']

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')

        rack_groups = (
            RackGroup.objects.create(name='Rack Group 1', slug='rack-group-1', site=site),
            RackGroup.objects.create(name='Rack Group 2', slug='rack-group-2', site=site),
            RackGroup.objects.create(name='Rack Group 3', slug='rack-group-3', site=site),
        )

        power_panels = (
            PowerPanel(site=site, rack_group=rack_groups[0], name='Power Panel 1'),
            PowerPanel(site=site, rack_group=rack_groups[1], name='Power Panel 2'),
            PowerPanel(site=site, rack_group=rack_groups[2], name='Power Panel 3'),
        )
        PowerPanel.objects.bulk_create(power_panels)

        cls.create_data = [
            {
                'name': 'Power Panel 4',
                'site': site.pk,
                'rack_group': rack_groups[0].pk,
            },
            {
                'name': 'Power Panel 5',
                'site': site.pk,
                'rack_group': rack_groups[1].pk,
            },
            {
                'name': 'Power Panel 6',
                'site': site.pk,
                'rack_group': rack_groups[2].pk,
            },
        ]


class PowerFeedTest(APIViewTestCases.APIViewTestCase):
    model = PowerFeed
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        rackgroup = RackGroup.objects.create(site=site, name='Rack Group 1', slug='rack-group-1')
        rackrole = RackRole.objects.create(name='Rack Role 1', slug='rack-role-1', color='ff0000')

        racks = (
            Rack(site=site, group=rackgroup, role=rackrole, name='Rack 1'),
            Rack(site=site, group=rackgroup, role=rackrole, name='Rack 2'),
            Rack(site=site, group=rackgroup, role=rackrole, name='Rack 3'),
            Rack(site=site, group=rackgroup, role=rackrole, name='Rack 4'),
        )
        Rack.objects.bulk_create(racks)

        power_panels = (
            PowerPanel(site=site, rack_group=rackgroup, name='Power Panel 1'),
            PowerPanel(site=site, rack_group=rackgroup, name='Power Panel 2'),
        )
        PowerPanel.objects.bulk_create(power_panels)

        PRIMARY = PowerFeedTypeChoices.TYPE_PRIMARY
        REDUNDANT = PowerFeedTypeChoices.TYPE_REDUNDANT
        power_feeds = (
            PowerFeed(power_panel=power_panels[0], rack=racks[0], name='Power Feed 1A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[0], name='Power Feed 1B', type=REDUNDANT),
            PowerFeed(power_panel=power_panels[0], rack=racks[1], name='Power Feed 2A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[1], name='Power Feed 2B', type=REDUNDANT),
            PowerFeed(power_panel=power_panels[0], rack=racks[2], name='Power Feed 3A', type=PRIMARY),
            PowerFeed(power_panel=power_panels[1], rack=racks[2], name='Power Feed 3B', type=REDUNDANT),
        )
        PowerFeed.objects.bulk_create(power_feeds)

        cls.create_data = [
            {
                'name': 'Power Feed 4A',
                'power_panel': power_panels[0].pk,
                'rack': racks[3].pk,
                'type': PRIMARY,
            },
            {
                'name': 'Power Feed 4B',
                'power_panel': power_panels[1].pk,
                'rack': racks[3].pk,
                'type': REDUNDANT,
            },
        ]
