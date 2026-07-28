import json
import re

import strawberry
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from strawberry.extensions import QueryDepthLimiter
from strawberry.schema.config import StrawberryConfig
from strawberry.types.nodes import FragmentSpread, InlineFragment, SelectedField

from dcim.choices import LocationStatusChoices
from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Location,
    Manufacturer,
    Rack,
    RackReservation,
    Site,
    VirtualChassis,
)
from extras.models import TableConfig, Tag
from ipam.models import IPAddress
from netbox.graphql.scalars import BigInt, BigIntScalar
from netbox.graphql.schema import Query, get_schema_extensions, schema
from utilities.tables import get_table_for_model
from utilities.testing import APITestCase, APIViewTestCases, TestCase, disable_warnings


class GraphQLTestCase(TestCase):

    def _schema_extension_instances(self):
        return [factory() for factory in get_schema_extensions()]

    @override_settings(GRAPHQL_ENABLED=False)
    def test_graphql_enabled(self):
        """
        The /graphql URL should return a 404 when GRAPHQL_ENABLED=False
        """
        url = reverse('graphql')
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

    def test_graphql_max_query_depth_disabled_by_default(self):
        """
        QueryDepthLimiter should not be installed when GRAPHQL_MAX_QUERY_DEPTH is unset.
        """
        self.assertFalse(any(isinstance(ext, QueryDepthLimiter) for ext in self._schema_extension_instances()))

    @override_settings(GRAPHQL_MAX_QUERY_DEPTH=0)
    def test_graphql_max_query_depth_disabled_when_zero(self):
        """
        QueryDepthLimiter should not be installed when GRAPHQL_MAX_QUERY_DEPTH is zero.
        """
        self.assertFalse(any(isinstance(ext, QueryDepthLimiter) for ext in self._schema_extension_instances()))

    @override_settings(GRAPHQL_MAX_QUERY_DEPTH=-1)
    def test_graphql_max_query_depth_disabled_when_negative(self):
        """
        QueryDepthLimiter should not be installed when GRAPHQL_MAX_QUERY_DEPTH is negative.
        """
        self.assertFalse(any(isinstance(ext, QueryDepthLimiter) for ext in self._schema_extension_instances()))

    @override_settings(GRAPHQL_MAX_QUERY_DEPTH=3)
    def test_graphql_max_query_depth_enforced(self):
        """
        Queries exceeding GRAPHQL_MAX_QUERY_DEPTH should be rejected.
        """
        extensions = get_schema_extensions()
        self.assertTrue(any(isinstance(ext, QueryDepthLimiter) for ext in self._schema_extension_instances()))

        # Build a temporary schema with the configured extension factories and execute a deep query
        test_schema = strawberry.Schema(
            query=Query,
            config=StrawberryConfig(auto_camel_case=False, scalar_map={BigInt: BigIntScalar}),
            extensions=extensions,
        )
        deep_query = '{ site_list { tenant { group { parent { parent { parent { name } } } } } } }'
        result = test_schema.execute_sync(deep_query)
        self.assertIsNotNone(result.errors)
        self.assertIn('exceeds maximum operation depth', str(result.errors[0]))

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphiql_interface(self):
        """
        Test rendering of the GraphiQL interactive web interface
        """
        url = reverse('graphql')
        header = {
            'HTTP_ACCEPT': 'text/html',
        }

        # Authenticated request
        response = self.client.get(url, **header)
        self.assertHttpStatus(response, 200)

        # Non-authenticated request
        self.client.logout()
        response = self.client.get(url, **header)
        with disable_warnings('django.request'):
            self.assertHttpStatus(response, 302)  # Redirect to login page

    def test_json_lookup_schema_is_string_backed(self):
        """JSONLookup date/time lookups keep the legacy string-backed input types and fields."""
        sdl = schema.as_str()

        def input_block(name):
            match = re.search(rf'^input {re.escape(name)}\b.*?^\}}', sdl, re.DOTALL | re.MULTILINE)
            self.assertIsNotNone(match, f'{name} not found in schema')
            return match.group(0)

        # JSONLookup points at the legacy string-backed lookup type names
        json_lookup = input_block('JSONLookup')
        self.assertIn('date_lookup: StrDateFilterLookup', json_lookup)
        self.assertIn('datetime_lookup: StrDatetimeFilterLookup', json_lookup)
        self.assertIn('time_lookup: StrTimeFilterLookup', json_lookup)

        # Value fields are string-backed, not Date/DateTime/Time scalars
        self.assertIn('exact: String', input_block('StrDateFilterLookup'))

        # Legacy date/time sub-lookups remain integer comparison lookups
        for name in ('StrTimeFilterLookup', 'StrDatetimeFilterLookup'):
            block = input_block(name)
            self.assertIn('date: IntComparisonFilterLookup', block)
            self.assertIn('time: IntComparisonFilterLookup', block)


class GraphQLAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
            Site(name='Site 4', slug='site-4'),
            Site(name='Site 5', slug='site-5'),
            Site(name='Site 6', slug='site-6'),
            Site(name='Site 7', slug='site-7'),
        )
        Site.objects.bulk_create(sites)

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_filter_objects(self):
        """
        Test the operation of filters for GraphQL API requests.
        """
        self.add_permissions('dcim.view_site', 'dcim.view_location')
        url = reverse('graphql')

        sites = Site.objects.all()[:3]
        Location.objects.create(
            site=sites[0],
            name='Location 1',
            slug='location-1',
            status=LocationStatusChoices.STATUS_PLANNED
        ),
        Location.objects.create(
            site=sites[1],
            name='Location 2',
            slug='location-2',
            status=LocationStatusChoices.STATUS_STAGING
        ),
        Location.objects.create(
            site=sites[1],
            name='Location 3',
            slug='location-3',
            status=LocationStatusChoices.STATUS_ACTIVE
        ),

        # A valid request should return the filtered list
        query = '{location_list(filters: {site_id: "' + str(sites[0].pk) + '"}) {id site {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['location_list']), 1)
        self.assertIsNotNone(data['data']['location_list'][0]['site'])

        # Test OR and exact logic
        query = """{
            location_list( filters: {
                status: {exact: STATUS_PLANNED},
                OR: {status: {exact: STATUS_STAGING}}
            }) {
                id site {id}
            }
        }"""
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['location_list']), 2)

        # Test in_list logic
        query = """{
            location_list( filters: {
                status: {in_list: [STATUS_PLANNED, STATUS_STAGING]}
            }) {
                id site {id}
            }
        }"""
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['location_list']), 2)

        # An invalid request should return an empty list
        query = '{location_list(filters: {site_id: "99999"}) {id site {id}}}'  # Invalid site ID
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['location_list']), 0)

        # Removing the permissions from location should result in an empty locations list
        self.remove_permissions('dcim.view_location')
        query = '{site(id: ' + str(sites[0].pk) + ') {id locations {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site']['locations']), 0)

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_nested_filter_objects(self):
        """
        Test filtering of nested GraphQL object lists.
        """
        self.add_permissions('dcim.view_site', 'dcim.view_location', 'extras.view_tag')

        site = Site.objects.create(
            name='Nested Filter Site',
            slug='nested-filter-site'
        )

        # Location is MPTT-managed; bulk_create skips tree-init hooks. Use per-instance create.
        Location.objects.create(
            site=site,
            name='Nested Active 1',
            slug='nested-active-1',
            status=LocationStatusChoices.STATUS_ACTIVE,
        )
        Location.objects.create(
            site=site,
            name='Nested Active 2',
            slug='nested-active-2',
            status=LocationStatusChoices.STATUS_ACTIVE,
        )
        Location.objects.create(
            site=site,
            name='Nested Planned',
            slug='nested-planned',
            status=LocationStatusChoices.STATUS_PLANNED,
        )

        planned = Tag.objects.create(name='Planned', slug='planned')
        production = Tag.objects.create(name='Production', slug='production')
        staging = Tag.objects.create(name='Staging', slug='staging')
        site.tags.add(planned, production, staging)

        url = reverse('graphql')
        query = f"""
        {{
          site(id: {site.pk}) {{
            locations(filters: {{status: {{exact: STATUS_ACTIVE}}}}) {{
              name
            }}
            tags(filters: {{name: {{i_starts_with: "P"}}}}) {{
              name
            }}
          }}
        }}
        """

        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        data = json.loads(response.content)
        self.assertNotIn('errors', data)

        self.assertEqual(
            {location['name'] for location in data['data']['site']['locations']},
            {'Nested Active 1', 'Nested Active 2'}
        )
        self.assertEqual(
            {tag['name'] for tag in data['data']['site']['tags']},
            {'Planned', 'Production'}
        )

    def test_graphql_integer_range_lookup(self):
        """
        Test that range_lookup works for integer fields (e.g. vc_position). Regression test for #20468.
        """
        self.add_permissions('dcim.view_device')
        url = reverse('graphql')

        manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device', slug='test-device')
        device_role = DeviceRole.objects.create(name='Test Role', slug='test-role')
        site = Site.objects.first()
        vc = VirtualChassis.objects.create(name='Test VC')

        devices = [
            Device(name=f'Device {i}', device_type=device_type, role=device_role, site=site,
                   virtual_chassis=vc, vc_position=i)
            for i in range(1, 6)
        ]
        Device.objects.bulk_create(devices)

        # range_lookup should return devices with vc_position between 2 and 4 inclusive
        query = """
        {
            device_list(filters: {vc_position: {range_lookup: {start: 2, end: 4}}}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['device_list']), 3)

    def test_graphql_array_length_lookup(self):
        """
        The public GraphQL ``length`` array lookup must map to Django's ``len`` transform.
        Regression test for #22766 using a standard array field (RackReservation.units).
        """
        self.add_permissions('dcim.view_rackreservation')
        url = reverse('graphql')

        site = Site.objects.first()
        rack = Rack.objects.create(name='Reservation Rack', site=site)
        RackReservation.objects.create(rack=rack, units=[1, 2], user=self.user, description='Two units')
        RackReservation.objects.create(rack=rack, units=[3, 4, 5], user=self.user, description='Three units')

        query = """
        {
            rack_reservation_list(filters: {units: {length: 2}}) {
                id units
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['rack_reservation_list']), 1)
        self.assertEqual(data['data']['rack_reservation_list'][0]['units'], [1, 2])

    def test_graphql_array_lookups(self):
        """
        The ``contains``, ``contained_by``, and ``overlap`` array lookups share their name with the
        corresponding ORM transform. Verify they still resolve after #22766 replaced the auto-generated
        filter fields with a manual ``filter()`` method.
        """
        self.add_permissions('dcim.view_rackreservation')
        url = reverse('graphql')

        site = Site.objects.first()
        rack = Rack.objects.create(name='Array Lookup Rack', site=site)
        RackReservation.objects.create(rack=rack, units=[1, 2], user=self.user, description='Low units')
        RackReservation.objects.create(rack=rack, units=[3, 4, 5], user=self.user, description='High units')

        def run(lookup):
            query = f"""
            {{
                rack_reservation_list(filters: {{units: {lookup}}}) {{
                    id units
                }}
            }}
            """
            response = self.client.post(url, data={'query': query}, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_200_OK)
            data = json.loads(response.content)
            self.assertNotIn('errors', data)
            return [r['units'] for r in data['data']['rack_reservation_list']]

        # contains: arrays that include all of the given elements
        self.assertEqual(run('{contains: [1]}'), [[1, 2]])
        # contained_by: arrays whose elements all fall within the given set
        self.assertEqual(run('{contained_by: [1, 2, 3]}'), [[1, 2]])
        # overlap: arrays sharing at least one element with the given set
        self.assertCountEqual(run('{overlap: [2, 3]}'), [[1, 2], [3, 4, 5]])

    def test_graphql_tableconfig_object_type_exposes_id(self):
        """TableConfigType.object_type must expose ContentType fields (e.g. id)."""
        self.add_permissions('extras.view_tableconfig')
        url = reverse('graphql')

        site_ct = ContentType.objects.get_for_model(Site)
        table_config = TableConfig.objects.create(
            object_type=site_ct,
            table=get_table_for_model(Site).__name__,
            name='Test config',
            columns=['name'],
        )

        query = '{ table_config(id: ' + str(table_config.pk) + ') { object_type { id } } }'
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(int(data['data']['table_config']['object_type']['id']), site_ct.pk)

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_device_list_tags_are_prefetched(self):
        """
        Requesting tags on device_list must batch tag lookups (no N+1 per device).
        """
        self.add_permissions('dcim.view_device', 'extras.view_tag')

        manufacturer = Manufacturer.objects.create(name='Prefetch Manufacturer', slug='prefetch-manufacturer')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Prefetch Model',
            slug='prefetch-model',
        )
        device_role = DeviceRole.objects.create(name='Prefetch Role', slug='prefetch-role')
        site = Site.objects.first()
        tag_alpha = Tag.objects.create(name='Prefetch Alpha', slug='prefetch-alpha')
        tag_beta = Tag.objects.create(name='Prefetch Beta', slug='prefetch-beta')

        devices = Device.objects.bulk_create([
            Device(
                name=f'Prefetch Device {index}',
                device_type=device_type,
                role=device_role,
                site=site,
            )
            for index in range(10)
        ])
        for device in devices:
            device.tags.set([tag_alpha, tag_beta])

        query = """
        {
            device_list(filters: {role: {slug: {exact: "prefetch-role"}}}) {
                name
                tags {
                    slug
                }
            }
        }
        """
        url = reverse('graphql')

        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['device_list']), 10)

        tag_queries = sum(1 for query_record in context.captured_queries if 'extras_tag' in query_record['sql'])
        self.assertLessEqual(
            tag_queries,
            2,
            msg=f'Expected batched tag prefetch, got {tag_queries} tag queries for 10 devices',
        )

    def test_graphql_ip_address_list_assigned_object_inline_fragment(self):
        """
        Requesting assigned_object via an inline fragment should batch prefetch.
        """
        self.add_permissions('ipam.view_ipaddress', 'dcim.view_interface', 'dcim.view_device')

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(name='Inline Fragment Manufacturer', slug='inline-fragment-mfg')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Inline Fragment Model',
            slug='inline-fragment-model',
        )
        device_role = DeviceRole.objects.create(name='Inline Fragment Role', slug='inline-fragment-role')
        device = Device.objects.create(
            name='Inline Fragment Device',
            site=site,
            device_type=device_type,
            role=device_role,
        )
        interface = Interface.objects.create(name='eth0', device=device, type='1000baset')
        ip_addresses = IPAddress.objects.bulk_create([
            IPAddress(address=f'192.0.2.{index}/24', assigned_object=interface)
            for index in range(1, 6)
        ])
        ip_ids = json.dumps([str(ip.pk) for ip in ip_addresses])

        query = f"""
        {{
            ip_address_list(filters: {{id: {{in_list: {ip_ids}}}}}) {{
                ... on IPAddressType {{
                    address
                    assigned_object {{
                        ... on InterfaceType {{
                            name
                            device {{
                                name
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        url = reverse('graphql')

        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['ip_address_list']), len(ip_addresses))

        device_queries = sum(1 for query_record in context.captured_queries if 'dcim_device' in query_record['sql'])
        self.assertLessEqual(
            device_queries,
            2,
            msg=f'Expected batched assigned_object prefetch, got {device_queries} device queries for 5 IP addresses',
        )

    def test_graphql_ip_address_list_assigned_object_fragment_spread(self):
        """
        Requesting assigned_object via a fragment spread should batch prefetch.
        """
        self.add_permissions('ipam.view_ipaddress', 'dcim.view_interface', 'dcim.view_device')

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(name='Fragment Spread Manufacturer', slug='fragment-spread-mfg')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Fragment Spread Model',
            slug='fragment-spread-model',
        )
        device_role = DeviceRole.objects.create(name='Fragment Spread Role', slug='fragment-spread-role')
        device = Device.objects.create(
            name='Fragment Spread Device',
            site=site,
            device_type=device_type,
            role=device_role,
        )
        interface = Interface.objects.create(name='eth0', device=device, type='1000baset')
        ip_addresses = IPAddress.objects.bulk_create([
            IPAddress(address=f'198.51.100.{index}/24', assigned_object=interface)
            for index in range(1, 6)
        ])
        ip_ids = json.dumps([str(ip.pk) for ip in ip_addresses])

        query = f"""
        fragment ipFields on IPAddressType {{
            address
            assigned_object {{
                ... on InterfaceType {{
                    device {{
                        name
                    }}
                }}
            }}
        }}
        {{
            ip_address_list(filters: {{id: {{in_list: {ip_ids}}}}}) {{
                ...ipFields
            }}
        }}
        """
        url = reverse('graphql')

        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['ip_address_list']), len(ip_addresses))

        device_queries = sum(1 for query_record in context.captured_queries if 'dcim_device' in query_record['sql'])
        self.assertLessEqual(
            device_queries,
            2,
            msg=f'Expected batched assigned_object prefetch, got {device_queries} device queries for 5 IP addresses',
        )

    def test_offset_pagination(self):
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')

        # Test `limit` only
        query = """
        {
            site_list(pagination: {limit: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 1')
        self.assertEqual(data['data']['site_list'][1]['name'], 'Site 2')
        self.assertEqual(data['data']['site_list'][2]['name'], 'Site 3')

        # Test `offset` only
        query = """
        {
            site_list(pagination: {offset: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 4)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 4')
        self.assertEqual(data['data']['site_list'][1]['name'], 'Site 5')
        self.assertEqual(data['data']['site_list'][2]['name'], 'Site 6')
        self.assertEqual(data['data']['site_list'][3]['name'], 'Site 7')

        # Test `offset` & `limit`
        query = """
        {
            site_list(pagination: {offset: 3, limit: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 4')
        self.assertEqual(data['data']['site_list'][1]['name'], 'Site 5')
        self.assertEqual(data['data']['site_list'][2]['name'], 'Site 6')

    def test_cursor_pagination(self):
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')

        # Page 1
        query = """
        {
            site_list(pagination: {start: 0, limit: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 1')
        self.assertEqual(data['data']['site_list'][1]['name'], 'Site 2')
        self.assertEqual(data['data']['site_list'][2]['name'], 'Site 3')

        # Page 2
        start_id = int(data['data']['site_list'][-1]['id']) + 1
        query = """
        {
            site_list(pagination: {start: """ + str(start_id) + """, limit: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 4')
        self.assertEqual(data['data']['site_list'][1]['name'], 'Site 5')
        self.assertEqual(data['data']['site_list'][2]['name'], 'Site 6')

        # Page 3
        start_id = int(data['data']['site_list'][-1]['id']) + 1
        query = """
        {
            site_list(pagination: {start: """ + str(start_id) + """, limit: 3}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 1)
        self.assertEqual(data['data']['site_list'][0]['name'], 'Site 7')

    @override_settings(MAX_PAGE_SIZE=3)
    def test_max_page_size(self):
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')

        # Request without explicit limit should be capped by MAX_PAGE_SIZE
        query = """
        {
            site_list {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)

        # Request with limit exceeding MAX_PAGE_SIZE should be capped
        query = """
        {
            site_list(pagination: {limit: 100}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 3)

        # Request with limit under MAX_PAGE_SIZE should be respected
        query = """
        {
            site_list(pagination: {limit: 2}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list']), 2)

    def test_pagination_conflict(self):
        url = reverse('graphql')
        query = """
        {
            site_list(pagination: {start: 1, offset: 1}) {
                id name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0]['message'], 'Cannot specify both `start` and `offset` in pagination.')


class GraphQLSchemaCoverageTestCase(APIViewTestCases.GraphQLSchemaCoverageTestCase):
    pass


class GraphQLSelectionTestCase(TestCase):
    """Unit tests for GraphQL selection field name collection."""

    def setUp(self):
        from types import SimpleNamespace

        from netbox.graphql.selections import get_selected_field_names

        self.get_selected_field_names = get_selected_field_names
        self.SimpleNamespace = SimpleNamespace

    def _info(self, selections):
        return self.SimpleNamespace(selected_fields=[self.SimpleNamespace(selections=selections)])

    def test_direct_fields(self):
        selections = [
            SelectedField(name='address', directives={}, arguments={}, selections=[]),
            SelectedField(name='assigned_object', directives={}, arguments={}, selections=[]),
        ]
        self.assertEqual(self.get_selected_field_names(self._info(selections)), {'address', 'assigned_object'})

    def test_inline_fragment(self):
        selections = [
            InlineFragment(
                type_condition='IPAddressType',
                directives={},
                selections=[
                    SelectedField(name='address', directives={}, arguments={}, selections=[]),
                    SelectedField(name='assigned_object', directives={}, arguments={}, selections=[]),
                ],
            ),
        ]
        self.assertEqual(self.get_selected_field_names(self._info(selections)), {'address', 'assigned_object'})

    def test_fragment_spread(self):
        selections = [
            FragmentSpread(
                name='ipFields',
                type_condition='IPAddressType',
                directives={},
                selections=[
                    SelectedField(name='address', directives={}, arguments={}, selections=[]),
                    SelectedField(name='assigned_object', directives={}, arguments={}, selections=[]),
                ],
            ),
        ]
        self.assertEqual(self.get_selected_field_names(self._info(selections)), {'address', 'assigned_object'})


class JSONPathValidationTestCase(TestCase):
    """Unit tests for _validate_json_path (VM-323 security fix)."""

    def setUp(self):
        from netbox.graphql.filter_lookups import _validate_json_path
        self.validate = _validate_json_path

    # --- Valid paths ---

    def test_single_key(self):
        self.assertEqual(self.validate('key'), 'key')

    def test_nested_key(self):
        self.assertEqual(self.validate('parent__child'), 'parent__child')

    def test_deeply_nested(self):
        self.assertEqual(self.validate('a__b__c'), 'a__b__c')

    def test_key_with_underscores(self):
        self.assertEqual(self.validate('my_key'), 'my_key')

    def test_key_with_hyphens(self):
        self.assertEqual(self.validate('my-key'), 'my-key')

    def test_numeric_array_index(self):
        self.assertEqual(self.validate('items__0'), 'items__0')

    def test_alphanumeric_segment(self):
        self.assertEqual(self.validate('key123'), 'key123')

    def test_key_with_leading_underscore(self):
        # JSON keys may start with underscore (e.g. _foo)
        self.assertEqual(self.validate('_key'), '_key')

    def test_orm_operator_name_as_key(self):
        # 'date', 'regex' etc. are valid JSON key names; the path validator
        # must not block them.  The ORM injection risk is neutralised by the
        # trailing __ that JSONFilter always appends before process_filters.
        self.assertEqual(self.validate('date'), 'date')
        self.assertEqual(self.validate('key__regex'), 'key__regex')
        self.assertEqual(self.validate('key__exact'), 'key__exact')

    # --- Invalid paths ---

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            self.validate('')

    def test_rejects_all_underscores(self):
        # '___' splits into segments ['', '', ''] via '__' — empty segments rejected
        with self.assertRaises(ValueError):
            self.validate('___')

    def test_accepts_trailing_single_underscore(self):
        # A single trailing underscore is a valid JSON key character
        self.assertEqual(self.validate('key_'), 'key_')

    def test_rejects_trailing_double_underscore(self):
        with self.assertRaises(ValueError):
            self.validate('key__')

    def test_rejects_leading_double_underscore(self):
        with self.assertRaises(ValueError):
            self.validate('__key')

    def test_rejects_consecutive_double_underscores(self):
        with self.assertRaises(ValueError):
            self.validate('key1____key2')

    def test_rejects_segment_starting_with_special_char(self):
        with self.assertRaises(ValueError):
            self.validate('$secret')

    def test_rejects_path_with_spaces(self):
        with self.assertRaises(ValueError):
            self.validate('key one')

    def test_rejects_path_with_dot(self):
        with self.assertRaises(ValueError):
            self.validate('key.subkey')


class JSONStringLookupTestCase(TestCase):
    """Verify JSONStringLookup exposes the expected set of string operators."""

    def test_string_operators_present(self):
        from netbox.graphql.filter_lookups import JSONStringLookup
        field_names = {f.name for f in JSONStringLookup.__strawberry_definition__.fields}
        for expected in ('exact', 'i_exact', 'contains', 'i_contains',
                         'starts_with', 'i_starts_with', 'ends_with', 'i_ends_with',
                         'in_', 'isnull', 'regex', 'i_regex'):
            self.assertIn(expected, field_names, f"{expected!r} must be present on JSONStringLookup")
