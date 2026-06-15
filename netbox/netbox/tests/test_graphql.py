import json
import re

import strawberry
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from strawberry.extensions import QueryDepthLimiter
from strawberry.schema.config import StrawberryConfig

from dcim.choices import LocationStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Location, Manufacturer, Site, VirtualChassis
from extras.models import TableConfig, Tag
from netbox.graphql.scalars import BigInt, BigIntScalar
from netbox.graphql.schema import Query, get_schema_extensions, schema
from utilities.tables import get_table_for_model
from utilities.testing import APITestCase, TestCase, disable_warnings


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
