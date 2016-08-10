import json
from rest_framework import status
from rest_framework.test import APITestCase


class SiteTest(APITestCase):

    fixtures = [
        'dcim',
        'ipam',
        'extras',
    ]

    standard_fields = [
        'id',
        'name',
        'slug',
        'tenant',
        'facility',
        'asn',
        'physical_address',
        'shipping_address',
        'comments',
        'count_prefixes',
        'count_vlans',
        'count_racks',
        'count_devices',
        'count_circuits'
    ]

    nested_fields = [
        'id',
        'name',
        'slug'
    ]

    rack_fields = [
        'id',
        'name',
        'facility_id',
        'display_name',
        'site',
        'group',
        'tenant',
        'role',
        'type',
        'width',
        'u_height',
        'comments'
    ]

    graph_fields = [
        'name',
        'embed_url',
        'embed_link',
    ]

    def test_get_list(self, endpoint='/api/dcim/sites/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/sites/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )

    def test_get_site_list_rack(self, endpoint='/api/dcim/sites/1/racks/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in json.loads(response.content):
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.rack_fields),
            )
            # Check Nested Serializer.
            self.assertEqual(
                sorted(i.get('site').keys()),
                sorted(self.nested_fields),
            )

    def test_get_site_list_graphs(self, endpoint='/api/dcim/sites/1/graphs/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in json.loads(response.content):
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.graph_fields),
            )


class RackTest(APITestCase):
    fixtures = [
        'dcim',
        'ipam'
    ]

    nested_fields = [
        'id',
        'name',
        'facility_id',
        'display_name'
    ]

    standard_fields = [
        'id',
        'name',
        'facility_id',
        'display_name',
        'site',
        'group',
        'tenant',
        'role',
        'type',
        'width',
        'u_height',
        'comments'
    ]

    detail_fields = [
        'id',
        'name',
        'facility_id',
        'display_name',
        'site',
        'group',
        'tenant',
        'role',
        'type',
        'width',
        'u_height',
        'comments',
        'front_units',
        'rear_units'
    ]

    def test_get_list(self, endpoint='/api/dcim/racks/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(i.get('site').keys()),
                sorted(SiteTest.nested_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/racks/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.detail_fields),
        )
        self.assertEqual(
            sorted(content.get('site').keys()),
            sorted(SiteTest.nested_fields),
        )


class ManufacturersTest(APITestCase):

    fixtures = [
        'dcim',
        'ipam'
    ]

    standard_fields = [
        'id',
        'name',
        'slug',
    ]

    nested_fields = standard_fields

    def test_get_list(self, endpoint='/api/dcim/manufacturers/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/manufacturers/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )


class DeviceTypeTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = [
        'id',
        'manufacturer',
        'model',
        'slug',
        'part_number',
        'u_height',
        'is_full_depth',
        'is_console_server',
        'is_pdu',
        'is_network_device',
    ]

    nested_fields = [
        'id',
        'manufacturer',
        'model',
        'slug'
    ]

    def test_get_list(self, endpoint='/api/dcim/device-types/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )

    def test_detail_list(self, endpoint='/api/dcim/device-types/1/'):
        # TODO: details returns list view.
        # response = self.client.get(endpoint)
        # content = json.loads(response.content)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(
        #     sorted(content.keys()),
        #     sorted(self.standard_fields),
        # )
        # self.assertEqual(
        #     sorted(content.get('manufacturer').keys()),
        #     sorted(ManufacturersTest.nested_fields),
        # )
        pass


class DeviceRolesTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'name', 'slug', 'color']

    nested_fields = ['id', 'name', 'slug']

    def test_get_list(self, endpoint='/api/dcim/device-roles/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/device-roles/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )


class PlatformsTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'name', 'slug', 'rpc_client']

    nested_fields = ['id', 'name', 'slug']

    def test_get_list(self, endpoint='/api/dcim/platforms/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/platforms/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )


class DeviceTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = [
        'id',
        'name',
        'display_name',
        'device_type',
        'device_role',
        'tenant',
        'platform',
        'serial',
        'rack',
        'position',
        'face',
        'parent_device',
        'status',
        'primary_ip',
        'primary_ip4',
        'primary_ip6',
        'comments',
    ]

    nested_fields = ['id', 'name', 'display_name']

    def test_get_list(self, endpoint='/api/dcim/devices/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for device in content:
            self.assertEqual(
                sorted(device.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(device.get('device_type')),
                sorted(DeviceTypeTest.nested_fields),
            )
            self.assertEqual(
                sorted(device.get('device_role')),
                sorted(DeviceRolesTest.nested_fields),
            )
            if device.get('platform'):
                self.assertEqual(
                    sorted(device.get('platform')),
                    sorted(PlatformsTest.nested_fields),
                )
            self.assertEqual(
                sorted(device.get('rack')),
                sorted(RackTest.nested_fields),
            )

    def test_get_list_flat(self, endpoint='/api/dcim/devices/?format=json_flat'):

        flat_fields = [
            'comments',
            'device_role_id',
            'device_role_name',
            'device_role_slug',
            'device_type_id',
            'device_type_manufacturer_id',
            'device_type_manufacturer_name',
            'device_type_manufacturer_slug',
            'device_type_model',
            'device_type_slug',
            'display_name',
            'face',
            'id',
            'name',
            'parent_device',
            'platform_id',
            'platform_name',
            'platform_slug',
            'position',
            'primary_ip_address',
            'primary_ip_family',
            'primary_ip_id',
            'primary_ip4_address',
            'primary_ip4_family',
            'primary_ip4_id',
            'primary_ip6',
            'rack_display_name',
            'rack_facility_id',
            'rack_id',
            'rack_name',
            'serial',
            'status',
            'tenant',
        ]

        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        device = content[0]
        self.assertEqual(
            sorted(device.keys()),
            sorted(flat_fields),
        )

    def test_get_detail(self, endpoint='/api/dcim/devices/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )


class ConsoleServerPortsTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'device', 'name', 'connected_console']

    nested_fields = ['id', 'device', 'name']

    def test_get_list(self, endpoint='/api/dcim/devices/9/console-server-ports/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for console_port in content:
            self.assertEqual(
                sorted(console_port.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(console_port.get('device')),
                sorted(DeviceTest.nested_fields),
            )


class ConsolePortsTest(APITestCase):
    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'device', 'name', 'cs_port', 'connection_status']

    nested_fields = ['id', 'device', 'name']

    def test_get_list(self, endpoint='/api/dcim/devices/1/console-ports/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for console_port in content:
            self.assertEqual(
                sorted(console_port.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(console_port.get('device')),
                sorted(DeviceTest.nested_fields),
            )
            self.assertEqual(
                sorted(console_port.get('cs_port')),
                sorted(ConsoleServerPortsTest.nested_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/console-ports/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )
        self.assertEqual(
            sorted(content.get('device')),
            sorted(DeviceTest.nested_fields),
        )


class PowerPortsTest(APITestCase):
    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']

    nested_fields = ['id', 'device', 'name']

    def test_get_list(self, endpoint='/api/dcim/devices/1/power-ports/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(i.get('device')),
                sorted(DeviceTest.nested_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/power-ports/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )
        self.assertEqual(
            sorted(content.get('device')),
            sorted(DeviceTest.nested_fields),
        )


class PowerOutletsTest(APITestCase):
    fixtures = ['dcim', 'ipam']

    standard_fields = ['id', 'device', 'name', 'connected_port']

    nested_fields = ['id', 'device', 'name']

    def test_get_list(self, endpoint='/api/dcim/devices/11/power-outlets/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(i.get('device')),
                sorted(DeviceTest.nested_fields),
            )


class InterfaceTest(APITestCase):
    fixtures = ['dcim', 'ipam', 'extras']

    standard_fields = [
        'id',
        'device',
        'name',
        'form_factor',
        'mac_address',
        'mgmt_only',
        'description',
        'is_connected'
    ]

    nested_fields = ['id', 'device', 'name']

    detail_fields = [
        'id',
        'device',
        'name',
        'form_factor',
        'mac_address',
        'mgmt_only',
        'description',
        'is_connected',
        'connected_interface'
    ]

    connection_fields = [
        'id',
        'interface_a',
        'interface_b',
        'connection_status',
    ]

    def test_get_list(self, endpoint='/api/dcim/devices/1/interfaces/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in content:
            self.assertEqual(
                sorted(i.keys()),
                sorted(self.standard_fields),
            )
            self.assertEqual(
                sorted(i.get('device')),
                sorted(DeviceTest.nested_fields),
            )

    def test_get_detail(self, endpoint='/api/dcim/interfaces/1/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.detail_fields),
        )
        self.assertEqual(
            sorted(content.get('device')),
            sorted(DeviceTest.nested_fields),
        )

    def test_get_graph_list(self, endpoint='/api/dcim/interfaces/1/graphs/'):
            response = self.client.get(endpoint)
            content = json.loads(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for i in content:
                self.assertEqual(
                    sorted(i.keys()),
                    sorted(SiteTest.graph_fields),
                )

    def test_get_interface_connections(self, endpoint='/api/dcim/interface-connections/4/'):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.connection_fields),
        )


class RelatedConnectionsTest(APITestCase):

    fixtures = ['dcim', 'ipam']

    standard_fields = [
        'device',
        'console-ports',
        'power-ports',
        'interfaces',
    ]

    def test_get_list(self, endpoint=(
            '/api/dcim/related-connections/'
            '?peer-device=test1-edge1&peer-interface=xe-0/0/3')):
        response = self.client.get(endpoint)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(content.keys()),
            sorted(self.standard_fields),
        )
