import json
import re
from unittest import mock, skipIf

import strawberry
import strawberry_django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from strawberry.extensions import QueryDepthLimiter
from strawberry.schema.config import StrawberryConfig

from core.models import ObjectType
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
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField, TableConfig, Tag
from ipam.models import RIR, Aggregate, IPAddress, Prefix
from netbox.graphql.pagination import apply_distinct_window_pagination
from netbox.graphql.scalars import BigInt, BigIntScalar
from netbox.graphql.schema import Query, get_schema_extensions, schema
from netbox.graphql.utils import register_model_graphql_type, splice_extension_bases, validate_extension_final_names
from netbox.registry import registry
from netbox.tests.dummy_plugin.models import DummySiteAttachment
from users.models import ObjectPermission, User
from utilities.tables import get_table_for_model
from utilities.testing import APITestCase, APIViewTestCases, TestCase, disable_warnings


def count_primary_table_queries(queries, table):
    """Count queries that read from `table` as the primary relation (not only as a join)."""
    pattern = re.compile(rf'FROM "{re.escape(table)}"')
    return sum(1 for query_record in queries if pattern.search(query_record['sql']))


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

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_plugin_extensions_execute(self):
        """
        A plugin-provided filter extension and field extension execute end-to-end against a live query,
        exercising the custom filter method's prefix plumbing and the type extension's resolver.
        """
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')

        query = '{ site_list(filters: {dummy_plugin_filter: "Site 1"}) { name dummy_plugin_field } }'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        sites = data['data']['site_list']
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]['name'], 'Site 1')
        self.assertEqual(sites[0]['dummy_plugin_field'], 'dummy-plugin-value')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_plugin_extension_preserves_get_queryset(self):
        """
        An extended core type keeps its own get_queryset() hook working, including its zero-argument super()
        call and the unit_count annotation.
        """
        site = Site.objects.create(name='Reservation Site', slug='reservation-site')
        rack = Rack.objects.create(name='Rack 1', site=site)
        RackReservation.objects.create(rack=rack, units=[1, 2, 3], user=self.user, description='Test')

        self.add_permissions('dcim.view_rackreservation')
        url = reverse('graphql')
        query = '{ rack_reservation_list { description units unit_count dummy_reservation_note } }'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        reservation = next(r for r in data['data']['rack_reservation_list'] if r['description'] == 'Test')
        self.assertEqual(reservation['unit_count'], 3)
        self.assertEqual(reservation['dummy_reservation_note'], 'dummy-reservation-note')

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_plugin_reverse_relation_scoped(self):
        """
        A plugin-provided reverse relation resolves through RestrictedPrefetch and returns only related objects
        the requesting user may view.
        """
        site = Site.objects.create(name='Attachment Site', slug='attachment-site')
        DummySiteAttachment.objects.create(site=site, name='Attachment A')
        DummySiteAttachment.objects.create(site=site, name='Attachment B')

        self.add_permissions('dcim.view_site')
        obj_perm = ObjectPermission(name='Attachment view', actions=['view'], constraints={'name': 'Attachment A'})
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(DummySiteAttachment))

        url = reverse('graphql')
        query = (
            '{ site_list(filters: {name: {exact: "Attachment Site"}}) '
            '{ name dummy_site_attachments { name } } }'
        )
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        attachments = data['data']['site_list'][0]['dummy_site_attachments']
        self.assertEqual([a['name'] for a in attachments], ['Attachment A'])

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, "dummy_plugin not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_plugin_schema_query_executes(self):
        """
        A plugin-provided top-level query field returning a core type executes, proving plugin schemas load
        at assembly time with extensions applied.
        """
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')
        query = '{ dummy_plugin_site_list { name dummy_plugin_field } }'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        site = next(s for s in data['data']['dummy_plugin_site_list'] if s['name'] == 'Site 1')
        self.assertEqual(site['dummy_plugin_field'], 'dummy-plugin-value')

    @skipIf('netbox.tests.dummy_plugin_b' not in settings.PLUGINS, "dummy_plugin_b not in settings.PLUGINS")
    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_cross_plugin_extension_applies(self):
        """
        An extension registered by a later plugin applies to a core type that an earlier plugin's schema
        module imports, proving later plugin extensions are registered before earlier plugin schemas load.
        """
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')
        query = '{ dummy_plugin_site_list { name dummy_plugin_b_field } }'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        site = next(s for s in data['data']['dummy_plugin_site_list'] if s['name'] == 'Site 1')
        self.assertEqual(site['dummy_plugin_b_field'], 'dummy-plugin-b-value')

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

    def test_graphql_custom_fields_include_unset_fields(self):
        """
        CustomFieldsMixin.custom_fields must emit a key for every custom field assigned to the model,
        as the REST API does, rather than returning the stored data verbatim. A key is materialized
        only once a value is assigned, so an object predating a field carries none; without this such
        a field would be absent from the response instead of null. Stale data for a field which no
        longer applies is likewise omitted.
        """
        self.add_permissions('dcim.view_site')
        url = reverse('graphql')

        cf = CustomField.objects.create(name='cf1', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf.object_types.set([ObjectType.objects.get_for_model(Site)])

        site = Site.objects.get(slug='site-1')
        self.assertNotIn('cf1', site.custom_field_data)
        Site.objects.filter(pk=site.pk).update(custom_field_data={'stale': 'value'})

        query = '{ site(id: ' + str(site.pk) + ') { custom_fields } }'
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(data['data']['site']['custom_fields'], {'cf1': None})

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

    def test_graphql_ip_address_list_assigned_object(self):
        """
        Requesting assigned_object should batch prefetch related objects.
        """
        self.add_permissions('ipam.view_ipaddress', 'dcim.view_interface', 'dcim.view_device')

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(name='Assigned Object Manufacturer', slug='assigned-object-mfg')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Assigned Object Model',
            slug='assigned-object-model',
        )
        device_role = DeviceRole.objects.create(name='Assigned Object Role', slug='assigned-object-role')
        device = Device.objects.create(
            name='Assigned Object Device',
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
        """
        url = reverse('graphql')

        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['ip_address_list']), len(ip_addresses))

        device_queries = count_primary_table_queries(context.captured_queries, 'dcim_device')
        self.assertLessEqual(
            device_queries,
            2,
            msg=f'Expected batched assigned_object prefetch, got {device_queries} device queries for 5 IP addresses',
        )

    def test_graphql_ip_address_list_assigned_object_nested_site(self):
        """
        Nested assigned_object selections should be optimized on the GFK prefetch queryset.
        """
        self.add_permissions(
            'ipam.view_ipaddress',
            'dcim.view_interface',
            'dcim.view_device',
            'dcim.view_site',
        )

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(
            name='Nested Site Manufacturer',
            slug='nested-site-mfg',
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Nested Site Model',
            slug='nested-site-model',
        )
        device_role = DeviceRole.objects.create(name='Nested Site Role', slug='nested-site-role')
        interfaces = []
        for index in range(5):
            device = Device.objects.create(
                name=f'Nested Site Device {index}',
                site=site,
                device_type=device_type,
                role=device_role,
            )
            interfaces.append(Interface.objects.create(
                name=f'eth{index}',
                device=device,
                type='1000baset',
            ))
        ip_addresses = IPAddress.objects.bulk_create([
            IPAddress(address=f'192.0.2.{index}/24', assigned_object=interfaces[index - 1])
            for index in range(1, 6)
        ])
        ip_ids = json.dumps([str(ip.pk) for ip in ip_addresses])

        query = f"""
        {{
            ip_address_list(filters: {{id: {{in_list: {ip_ids}}}}}) {{
                address
                assigned_object {{
                    ... on InterfaceType {{
                        name
                        device {{
                            name
                            site {{
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
        for ip_data in data['data']['ip_address_list']:
            self.assertEqual(ip_data['assigned_object']['device']['site']['name'], site.name)

        device_queries = count_primary_table_queries(context.captured_queries, 'dcim_device')
        site_queries = count_primary_table_queries(context.captured_queries, 'dcim_site')
        self.assertLessEqual(
            device_queries,
            2,
            msg=f'Expected batched device prefetch, got {device_queries} device queries for 5 IP addresses',
        )
        self.assertLessEqual(
            site_queries,
            2,
            msg=f'Expected optimized site join, got {site_queries} site queries for 5 IP addresses',
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

    def test_to_one_relation_prefetch(self):
        """
        A prefetched to-one relation should be fetched with a plain `WHERE id IN (...)` query, rather than
        with a window function partitioned by the parent ID (which returns every row sharing the related
        object, regardless of the requested page size).
        """
        self.add_permissions('dcim.view_device', 'dcim.view_site')
        url = reverse('graphql')

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        Device.objects.bulk_create([
            Device(name=f'Device {i}', site=site, device_type=device_type, role=role)
            for i in range(1, 21)
        ])

        # Request two of the twenty devices at the site
        query = """
        {
            device_list(pagination: {limit: 2}) {
                name
                site { name }
            }
        }
        """
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['device_list']), 2)
        self.assertEqual(data['data']['device_list'][0]['site']['name'], site.name)

        # The site should have been fetched by exactly one query. (Asserting that it exists keeps the
        # assertions below from silently passing if the site is ever fetched some other way.)
        site_queries = [q['sql'] for q in ctx.captured_queries if 'FROM "dcim_site"' in q['sql']]
        self.assertEqual(len(site_queries), 1, msg=f'Expected one query against dcim_site, got {site_queries}')

        # That query should not apply window pagination, nor join back to the devices table (which would
        # return one row per device at the site)
        self.assertNotIn('ROW_NUMBER', site_queries[0])
        self.assertNotIn('dcim_device', site_queries[0])

    @override_settings(MAX_PAGE_SIZE=3)
    def test_max_page_size_nested_list(self):
        """
        MAX_PAGE_SIZE should still be enforced on a nested list relation.
        """
        self.add_permissions('dcim.view_device', 'dcim.view_site')
        url = reverse('graphql')

        site = Site.objects.first()
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        Device.objects.bulk_create([
            Device(name=f'Device {i}', site=site, device_type=device_type, role=role)
            for i in range(1, 6)
        ])

        query = """
        {
            site_list(pagination: {limit: 1}) {
                name
                devices { name }
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site_list'][0]['devices']), 3)

    def test_distinct_nested_list(self):
        """
        The `DISTINCT` filter should deduplicate a nested list field which is filtered across a to-many
        relation, just as it does for the equivalent top-level list field.
        """
        self.add_permissions('dcim.view_device', 'dcim.view_site')
        url = reverse('graphql')

        site = Site.objects.get(slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        devices = Device.objects.bulk_create([
            Device(name=f'Device {i}', site=site, device_type=device_type, role=role)
            for i in range(1, 3)
        ])
        Interface.objects.bulk_create([
            Interface(device=device, name=f'eth{i}', type='1000base-t')
            for device in devices
            for i in range(3)
        ])

        # Each device should be returned exactly once, despite having three matching interfaces
        query = """
        {
            site_list(filters: {slug: {exact: "site-1"}}) {
                name
                devices(filters: {DISTINCT: true, interfaces: {name: {starts_with: "eth"}}}) {
                    name
                }
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(
            [device['name'] for device in data['data']['site_list'][0]['devices']],
            ['Device 1', 'Device 2']
        )

        # The equivalent top-level query should return the same devices
        query = """
        {
            device_list(filters: {DISTINCT: true, interfaces: {name: {starts_with: "eth"}}}) {
                name
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(
            [device['name'] for device in data['data']['device_list']],
            ['Device 1', 'Device 2']
        )

    @override_settings(MAX_PAGE_SIZE=2)
    def test_distinct_nested_list_max_page_size(self):
        """
        MAX_PAGE_SIZE should still be enforced on a deduplicated nested list field, and should be applied
        to the number of distinct objects returned (not to the number of joined rows).
        """
        self.add_permissions('dcim.view_device', 'dcim.view_site')
        url = reverse('graphql')

        site = Site.objects.get(slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        devices = Device.objects.bulk_create([
            Device(name=f'Device {i}', site=site, device_type=device_type, role=role)
            for i in range(1, 5)
        ])
        Interface.objects.bulk_create([
            Interface(device=device, name=f'eth{i}', type='1000base-t')
            for device in devices
            for i in range(3)
        ])

        query = """
        {
            site_list(filters: {slug: {exact: "site-1"}}) {
                name
                devices(filters: {DISTINCT: true, interfaces: {name: {starts_with: "eth"}}}) {
                    name
                }
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(
            [device['name'] for device in data['data']['site_list'][0]['devices']],
            ['Device 1', 'Device 2']
        )

        # An explicit offset should likewise be applied to the distinct objects
        query = """
        {
            site_list(filters: {slug: {exact: "site-1"}}) {
                name
                devices(
                    pagination: {offset: 1, limit: 2},
                    filters: {DISTINCT: true, interfaces: {name: {starts_with: "eth"}}}
                ) {
                    name
                }
            }
        }
        """
        response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(
            [device['name'] for device in data['data']['site_list'][0]['devices']],
            ['Device 2', 'Device 3']
        )

    def test_distinct_window_pagination_tied_ordering(self):
        """
        Two rows which represent *different* objects must never be assigned the same rank, even when they
        compare equal under the queryset's ordering. `DENSE_RANK()` ties such rows by definition, so the
        primary key is appended to the window ordering to separate them; without it every device below
        would be assigned rank 1 and the limit of two would return all four of them.
        """
        site = Site.objects.get(slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        devices = Device.objects.bulk_create([
            Device(name=f'Device {i}', site=site, device_type=device_type, role=role)
            for i in range(1, 5)
        ])
        Interface.objects.bulk_create([
            Interface(device=device, name=f'eth{i}', type='1000base-t')
            for device in devices
            for i in range(3)
        ])

        # Order by a column whose value is identical for every device, so that the ordering alone cannot
        # distinguish them. Each device additionally matches three interfaces, so the join emits three
        # duplicate rows per device which DISTINCT must still collapse.
        queryset = Device.objects.filter(
            site=site, interfaces__name__startswith='eth'
        ).order_by('status').distinct()
        queryset = apply_distinct_window_pagination(queryset, related_field_id='site_id', limit=2)

        results = list(queryset)
        self.assertEqual(sorted(device.name for device in results), ['Device 1', 'Device 2'])
        self.assertEqual(sorted(device._strawberry_row_number for device in results), [1, 2])

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


class GraphQLDeferredColumnTestCase(APITestCase):
    """
    A GraphQL field backed by a custom resolver is opaque to the query optimizer, which narrows column
    selection with .only() based on the fields named in the GraphQL document. Any column such a resolver
    reads must therefore be declared via an `only` hint; otherwise the column is deferred and reading it
    reloads the row from the database once per object returned (see #22813).

    Each test below asserts both that no single-row reload occurs and that the model's table is read
    exactly once per request, regardless of the number of objects returned.
    """
    OBJECT_COUNT = 10

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')

        # Devices, for CustomFieldsMixin.custom_fields
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        custom_field = CustomField.objects.create(name='cf1', type=CustomFieldTypeChoices.TYPE_TEXT)
        custom_field.object_types.set([ObjectType.objects.get_for_model(Device)])
        Device.objects.bulk_create([
            Device(
                name=f'Device {i}',
                device_type=device_type,
                role=device_role,
                site=site,
                custom_field_data={'cf1': f'value {i}'},
            )
            for i in range(cls.OBJECT_COUNT)
        ])

        # Rack reservations, for RackReservationType.unit_count. Reservations within a rack may not claim
        # overlapping units, so each is allocated a distinct run of them. The length of each run varies so
        # that unit_count is asserted per object rather than against a single expected value.
        rack = Rack.objects.create(name='Rack 1', site=site)
        user = User.objects.create(username='Reservation user')
        reservations, next_unit = [], 1
        for i in range(cls.OBJECT_COUNT):
            unit_count = i % 3 + 1
            reservations.append(RackReservation(
                rack=rack,
                units=list(range(next_unit, next_unit + unit_count)),
                user=user,
                description=f'Reservation {i}',
            ))
            next_unit += unit_count
        cls.expected_unit_counts = {
            reservation.pk: len(reservation.units)
            for reservation in RackReservation.objects.bulk_create(reservations)
        }
        # IPAM objects, for the `family` field of each type which exposes one
        IPAddress.objects.bulk_create([
            IPAddress(address=f'10.0.0.{i + 1}/24') for i in range(cls.OBJECT_COUNT)
        ])
        Prefix.objects.bulk_create([
            Prefix(prefix=f'10.{i}.0.0/16') for i in range(cls.OBJECT_COUNT)
        ])
        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        Aggregate.objects.bulk_create([
            Aggregate(prefix=f'{i + 20}.0.0.0/8', rir=rir) for i in range(cls.OBJECT_COUNT)
        ])

    def _execute(self, query):
        url = reverse('graphql')
        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, data={'query': query}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        return data['data'], context.captured_queries

    def assertNoDeferredColumnReloads(self, query_template, list_field, table, validate):
        """
        Execute `query_template` (which must accept a `limit` interpolation) for a single object and for
        OBJECT_COUNT objects, asserting that no row of `table` is re-fetched by primary key and that the
        table is read exactly once per request regardless of the number of objects returned. `validate`
        is called with the returned objects.

        Assert on the number of reads of `table` rather than on the total query count: the capture window
        also holds request processing queries which may be repeated when a cache key shared by the other
        parallel test workers is evicted mid-test, which would otherwise fail the test spuriously.
        """
        for limit in (1, self.OBJECT_COUNT):
            data, queries = self._execute(query_template % {'limit': limit})
            objects = data[list_field]
            self.assertEqual(len(objects), limit)
            validate(objects)

            reloads = [q['sql'] for q in queries if f'FROM "{table}" WHERE "{table}"."id" = ' in q['sql']]
            self.assertEqual(
                reloads, [], msg=f'{len(reloads)} deferred-column reload(s) for {limit} object(s): {reloads[:1]}'
            )

            reads = [q['sql'] for q in queries if f'FROM "{table}"' in q['sql']]
            self.assertEqual(
                len(reads), 1,
                msg=f'{table} must be read once for {limit} object(s), got {len(reads)} read(s): {reads}'
            )

    def test_custom_fields(self):
        """
        Regression test for #22813: CustomFieldsMixin.custom_fields must not defer `custom_field_data`.
        """
        self.add_permissions('dcim.view_device')
        query = """
        {
            device_list(pagination: {limit: %(limit)s}) {
                id
                custom_fields
            }
        }
        """

        expected_values = {f'value {i}' for i in range(self.OBJECT_COUNT)}

        def validate(devices):
            for device in devices:
                self.assertEqual(list(device['custom_fields']), ['cf1'])
                self.assertIn(device['custom_fields']['cf1'], expected_values)

        self.assertNoDeferredColumnReloads(query, 'device_list', 'dcim_device', validate)

    def test_rack_reservation_unit_count(self):
        """
        Regression test for #22822: RackReservationType.unit_count must not defer `units`.
        """
        self.add_permissions('dcim.view_rackreservation')
        query = """
        {
            rack_reservation_list(pagination: {limit: %(limit)s}) {
                id
                unit_count
            }
        }
        """

        def validate(reservations):
            for reservation in reservations:
                self.assertEqual(
                    reservation['unit_count'], self.expected_unit_counts[int(reservation['id'])]
                )

        self.assertNoDeferredColumnReloads(query, 'rack_reservation_list', 'dcim_rackreservation', validate)

    def test_ip_address_family(self):
        """
        Regression test for #22823: IPAddressType.family must not defer `address`.
        """
        self.add_permissions('ipam.view_ipaddress')
        query = """
        {
            ip_address_list(pagination: {limit: %(limit)s}) {
                id
                family { value label }
            }
        }
        """
        self.assertNoDeferredColumnReloads(
            query, 'ip_address_list', 'ipam_ipaddress', self._validate_ipv4_family
        )

    def test_prefix_family(self):
        """
        Regression test for #22823: PrefixType.family must not defer `prefix`.
        """
        self.add_permissions('ipam.view_prefix')
        query = """
        {
            prefix_list(pagination: {limit: %(limit)s}) {
                id
                family { value label }
            }
        }
        """
        self.assertNoDeferredColumnReloads(query, 'prefix_list', 'ipam_prefix', self._validate_ipv4_family)

    def test_aggregate_family(self):
        """
        Regression test for #22823: AggregateType.family must not defer `prefix`.
        """
        self.add_permissions('ipam.view_aggregate')
        query = """
        {
            aggregate_list(pagination: {limit: %(limit)s}) {
                id
                family { value label }
            }
        }
        """
        self.assertNoDeferredColumnReloads(query, 'aggregate_list', 'ipam_aggregate', self._validate_ipv4_family)

    def _validate_ipv4_family(self, objects):
        for obj in objects:
            self.assertEqual(obj['family'], {'value': 4, 'label': 'IPv4'})


class GraphQLSchemaCoverageTestCase(APIViewTestCases.GraphQLSchemaCoverageTestCase):
    pass


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


class SpliceExtensionBasesTestCase(TestCase):
    """Verify splice_extension_bases() composition and the strictly additive extension contract."""

    @staticmethod
    def _make_core():
        @strawberry.type
        class CoreBase:
            description: str  # inherited (non-protected) field

            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return queryset

        @strawberry.type
        class CoreType(CoreBase):
            name: str  # defined directly in the core type's own body

        return CoreType

    def test_no_extensions_is_passthrough(self):
        CoreType = self._make_core()
        self.assertIs(splice_extension_bases(CoreType, []), CoreType)
        self.assertIs(splice_extension_bases(CoreType, None), CoreType)

    def test_extension_spliced_into_bases(self):
        @strawberry.type
        class Extension:
            models = ['dcim.device']
            extra: str

        CoreType = self._make_core()
        result = splice_extension_bases(CoreType, [Extension])
        self.assertIsNot(result, CoreType)
        self.assertEqual(result.__name__, CoreType.__name__)
        self.assertIn(Extension, result.__mro__)
        self.assertTrue(issubclass(result, CoreType))
        # The extension is appended *after* the core bases in the MRO (additive, core wins collisions)
        self.assertGreater(result.__mro__.index(Extension), result.__mro__.index(CoreType.__bases__[0]))

    def test_extension_cannot_shadow_core_own_field(self):
        @strawberry.type
        class Extension:
            models = ['dcim.device']
            name: str

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [Extension])

    def test_extension_cannot_shadow_inherited_field(self):
        @strawberry.type
        class Extension:
            models = ['dcim.device']
            description: str

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [Extension])

    def test_extension_cannot_shadow_core_hook(self):
        @strawberry.type
        class Extension:
            models = ['dcim.device']

            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return queryset

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [Extension])

    def test_two_extensions_cannot_declare_same_new_field(self):
        @strawberry.type
        class ExtensionA:
            models = ['dcim.device']
            widgets: str

        @strawberry.type
        class ExtensionB:
            models = ['dcim.device']
            widgets: str

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [ExtensionA, ExtensionB])

    def test_extension_cannot_interleave_ahead_of_core_ancestor(self):
        """Shared ancestry is rejected because C3 could resolve an inherited hook to the extension side."""
        class CoreBase:
            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return 'core'

        class CoreType(CoreBase):
            pass

        class ExtensionBase(CoreBase):
            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return 'plugin'

        @strawberry.type
        class Extension(ExtensionBase):
            models = ['dcim.site']

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(CoreType, [Extension])

    def test_extension_cannot_inherit_core_hook_name(self):
        """An inherited plain method colliding with a core name fails instead of being silently ignored."""
        class PluginBase:
            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return queryset

        @strawberry.type
        class Extension(PluginBase):
            models = ['dcim.site']

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [Extension])

    def test_extensions_may_share_a_helper_base(self):
        """Two extensions inheriting the same helper method compose without a collision error."""
        class Helper:
            @classmethod
            def _helper(cls):
                return 'x'

        @strawberry.type
        class ExtensionA(Helper):
            models = ['dcim.site']
            field_a: str

        @strawberry.type
        class ExtensionB(Helper):
            models = ['dcim.site']
            field_b: str

        composed = splice_extension_bases(self._make_core(), [ExtensionA, ExtensionB])
        self.assertTrue(issubclass(composed, ExtensionA))

    def test_extension_may_inherit_annotation_only_name_from_plain_base(self):
        """An annotation on a plain base is neither a Strawberry field nor an attribute, so it shadows nothing."""
        class Helper:
            name: str

        @strawberry.type
        class Extension(Helper):
            models = ['dcim.site']
            plugin_field: str

        composed = splice_extension_bases(self._make_core(), [Extension])
        self.assertTrue(issubclass(composed, Extension))

    def test_extensions_may_share_a_plain_annotated_helper_base(self):
        """Two extensions inheriting one annotation-only helper base do not collide with each other."""
        class Helper:
            internal_state: str

        @strawberry.type
        class ExtensionA(Helper):
            models = ['dcim.site']
            field_a: str

        @strawberry.type
        class ExtensionB(Helper):
            models = ['dcim.site']
            field_b: str

        composed = splice_extension_bases(self._make_core(), [ExtensionA, ExtensionB])
        self.assertTrue(issubclass(composed, ExtensionA))
        self.assertTrue(issubclass(composed, ExtensionB))

    def test_two_extensions_cannot_bind_the_same_helper_function(self):
        """Sharing one base is legal, but two declarations of a name are not, even for the same function object."""
        def shared_helper(self):
            return 'x'

        @strawberry.type
        class ExtensionA:
            models = ['dcim.site']
            field_a: str
            helper = shared_helper

        @strawberry.type
        class ExtensionB:
            models = ['dcim.site']
            field_b: str
            helper = shared_helper

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [ExtensionA, ExtensionB])

    def test_extension_cannot_inherit_field_named_for_core_hook(self):
        """A field inherited from a decorated base still collides with a core name that is only a plain hook."""
        @strawberry.type
        class ExtensionBase:
            get_queryset: str

        @strawberry.type
        class Extension(ExtensionBase):
            models = ['dcim.site']

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [Extension])

    def test_extensions_cannot_collide_via_inherited_field_and_plain_method(self):
        """One extension's inherited Strawberry field collides with another's plain method of the same name."""
        @strawberry.type
        class BaseWithField:
            shared: str

        @strawberry.type
        class ExtensionA(BaseWithField):
            models = ['dcim.site']

        @strawberry.type
        class ExtensionB:
            models = ['dcim.site']

            def shared(self):
                return 'x'

        with self.assertRaises(ImproperlyConfigured):
            splice_extension_bases(self._make_core(), [ExtensionA, ExtensionB])

    def test_conflicting_extension_bases_raise_clear_error(self):
        class A:
            pass

        class B:
            pass

        class Core:
            name = 'core'

        @strawberry.type
        class Ext1(A, B):
            models = ['dcim.device']
            field_1: str

        @strawberry.type
        class Ext2(B, A):
            models = ['dcim.device']
            field_2: str

        with self.assertRaises(ImproperlyConfigured) as ctx:
            splice_extension_bases(Core, [Ext1, Ext2])
        self.assertIn('Failed to compose', str(ctx.exception))

    def test_zero_arg_super_and_own_fields_survive_composition(self):
        """Composition preserves the core class's own annotated fields and its zero-argument super() calls."""
        @strawberry.type
        class Extension:
            models = ['dcim.rackreservation']

            @strawberry_django.field
            def extension_field(self) -> str:
                return 'x'

        @strawberry.type
        class CoreBase:
            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return queryset

        class RackReservationProto(CoreBase):
            units: list[int]
            description: str

            @classmethod
            def get_queryset(cls, queryset, info, **kwargs):
                return super().get_queryset(queryset, info, **kwargs)

        core_type = strawberry_django.type(RackReservation, fields='__all__')(RackReservationProto)
        composed = splice_extension_bases(core_type, [Extension])
        self.assertTrue(issubclass(composed, RackReservationProto))
        result = strawberry_django.type(RackReservation, fields='__all__')(composed)
        names = {f.name for f in result.__strawberry_definition__.fields}
        self.assertIn('units', names)
        self.assertIn('description', names)
        self.assertIn('extension_field', names)
        self.assertIs(result.get_queryset('QS', None), 'QS')

    def test_extension_cannot_replace_generated_model_field(self):
        @strawberry.type
        class CoreBase:
            pass

        class CoreType(CoreBase):
            pass

        @strawberry.type
        class Extension:
            models = ['dcim.site']
            name: str

        core_type = strawberry_django.type(Site, fields='__all__')(CoreType)
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_type, [Extension])

    def test_extension_cannot_alias_onto_existing_name(self):
        @strawberry.type
        class Extension:
            models = ['dcim.site']

            @strawberry.field(name='description')
            def plugin_description(self) -> str:
                return 'x'

        core_type = strawberry_django.type(Site, fields='__all__')(self._make_core())
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_type, [Extension])

    def test_extension_cannot_alias_away_generated_model_field(self):
        """An aliased extension field still claims its python name, which would suppress the generated field."""
        @strawberry.type
        class Extension:
            models = ['dcim.site']
            slug: str = strawberry.field(name='plugin_slug')

        core_type = strawberry_django.type(Site, fields='__all__')(self._make_core())
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_type, [Extension])

    def test_filter_extension_cannot_alias_away_core_filter_field(self):
        """The python-name check applies to the filter path as well."""
        class CoreFilter:
            name: str | None = strawberry_django.filter_field()

        @strawberry.type
        class Extension:
            models = ['dcim.site']
            name: str | None = strawberry_django.filter_field(name='plugin_name')

        core_filter = strawberry_django.filter_type(Site, lookups=True)(CoreFilter)
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_filter, [Extension])

    def test_filter_extension_cannot_alias_away_logical_field(self):
        """A generated logical filter field is protected from python-name capture through an alias."""
        class CoreFilter:
            pass

        @strawberry.type
        class Extension:
            models = ['dcim.site']
            AND: str | None = strawberry_django.filter_field(name='plugin_and')

        core_filter = strawberry_django.filter_type(Site, lookups=True)(CoreFilter)
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_filter, [Extension])

    def test_extension_cannot_alias_onto_core_filter_alias(self):
        class CoreFilter:
            _custom: str | None = strawberry_django.filter_field(name='custom')

        @strawberry.type
        class Extension:
            models = ['dcim.site']
            custom: str | None = strawberry_django.filter_field()

        core_filter = strawberry_django.filter_type(Site, lookups=True)(CoreFilter)
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_filter, [Extension])

    def test_extension_cannot_redefine_filter_logical_fields(self):
        class CoreFilter:
            pass

        @strawberry.type
        class Extension:
            models = ['dcim.site']
            AND: str | None = None

        core_filter = strawberry_django.filter_type(Site, lookups=True)(CoreFilter)
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_filter, [Extension])

    def test_two_extensions_cannot_inherit_same_python_name(self):
        """Inherited fields collide by python name even when their GraphQL aliases differ."""
        @strawberry.type
        class ExtensionBaseA:
            value: str = strawberry.field(name='plugin_a_value')

        @strawberry.type
        class ExtensionA(ExtensionBaseA):
            models = ['dcim.site']

        @strawberry.type
        class ExtensionBaseB:
            value: str = strawberry.field(name='plugin_b_value')

        @strawberry.type
        class ExtensionB(ExtensionBaseB):
            models = ['dcim.site']

        core_type = strawberry_django.type(Site, fields='__all__')(self._make_core())
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_type, [ExtensionA, ExtensionB])

    def test_extension_composition_preserves_core_is_type_of(self):
        """A core-defined is_type_of survives composition instead of being shadowed by the injected default."""
        @strawberry.type
        class Extension:
            models = ['dcim.rackreservation']

            @strawberry_django.field
            def marker_field(self) -> str:
                return 'x'

        @strawberry.type
        class CoreBase:
            pass

        class Proto(CoreBase):
            @classmethod
            def is_type_of(cls, obj, info):
                return True

        custom = vars(Proto)['is_type_of']
        with mock.patch.dict(registry['plugins']['graphql_type_extensions'], {'dcim.rackreservation': [Extension]}):
            final = register_model_graphql_type(
                RackReservation, strawberry_django.type, 'graphql_type_extensions', fields='__all__'
            )(Proto)
        self.assertIs(vars(final).get('is_type_of'), custom)

    def test_defaulted_extension_field_composes_onto_required_core_fields(self):
        """Strawberry keyword-only fields let a defaulted extension field precede required core fields."""
        @strawberry.type
        class Extension:
            models = ['dcim.rackreservation']
            plugin_note: str = strawberry.field(default='note')

        @strawberry.type
        class Proto:
            pass

        with mock.patch.dict(registry['plugins']['graphql_type_extensions'], {'dcim.rackreservation': [Extension]}):
            final = register_model_graphql_type(
                RackReservation, strawberry_django.type, 'graphql_type_extensions', fields='__all__'
            )(Proto)
        names = {field.python_name for field in final.__strawberry_definition__.fields}
        self.assertIn('plugin_note', names)
        self.assertIn('units', names)

    def test_two_extensions_cannot_alias_same_final_name(self):
        @strawberry.type
        class ExtensionA:
            models = ['dcim.site']
            widgets: str

        @strawberry.type
        class ExtensionB:
            models = ['dcim.site']

            @strawberry.field(name='widgets')
            def other_name(self) -> str:
                return 'x'

        core_type = strawberry_django.type(Site, fields='__all__')(self._make_core())
        with self.assertRaises(ImproperlyConfigured):
            validate_extension_final_names(core_type, [ExtensionA, ExtensionB])
