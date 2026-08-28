"""
Unit tests for OpenAPI schema generation.

Refs: #20638
"""
import json

from django.test import SimpleTestCase, TestCase

from core.api.schema import FixSerializedPKRelatedField
from dcim.api.serializers import SiteSerializer
from dcim.models import Site
from netbox.api.fields import SerializedPKRelatedField


class OpenAPISchemaTestCase(TestCase):
    """Tests for OpenAPI schema generation."""

    @classmethod
    def setUpClass(cls):
        """
        Fetch the schema via the API endpoint. Schema generation is expensive and its output is
        immutable across these tests, so do this once for the class rather than per test method.
        """
        super().setUpClass()

        response = cls.client_class().get('/api/schema/', {'format': 'json'})
        assert response.status_code == 200, f'Failed to generate OpenAPI schema (HTTP {response.status_code})'
        cls.schema = json.loads(response.content)

    def test_post_operation_documents_single_or_array(self):
        """
        POST operations on NetBoxModelViewSet endpoints should document
        support for both single objects and arrays via oneOf.

        Refs: #20638
        """
        # Test representative endpoints across different apps
        test_paths = [
            '/api/core/data-sources/',
            '/api/dcim/sites/',
            '/api/users/users/',
            '/api/ipam/ip-addresses/',
        ]

        for path in test_paths:
            with self.subTest(path=path):
                operation = self.schema['paths'][path]['post']

                # Get the request body schema
                request_schema = operation['requestBody']['content']['application/json']['schema']

                # Should have oneOf with two options
                self.assertIn('oneOf', request_schema, f"POST {path} should have oneOf schema")
                self.assertEqual(
                    len(request_schema['oneOf']), 2,
                    f"POST {path} oneOf should have exactly 2 options"
                )

                # First option: single object (has $ref or properties)
                single_schema = request_schema['oneOf'][0]
                self.assertTrue(
                    '$ref' in single_schema or 'properties' in single_schema,
                    f"POST {path} first oneOf option should be single object"
                )

                # Second option: array of objects
                array_schema = request_schema['oneOf'][1]
                self.assertEqual(
                    array_schema['type'], 'array',
                    f"POST {path} second oneOf option should be array"
                )
                self.assertIn('items', array_schema, f"POST {path} array should have items")

    def test_bulk_update_operations_require_array_only(self):
        """
        Bulk update/patch operations should require arrays only, not oneOf.
        They don't support single object input.

        Refs: #20638
        """
        test_paths = [
            '/api/dcim/sites/',
            '/api/users/users/',
        ]

        for path in test_paths:
            for method in ['put', 'patch']:
                with self.subTest(path=path, method=method):
                    operation = self.schema['paths'][path][method]
                    request_schema = operation['requestBody']['content']['application/json']['schema']

                    # Should be array-only, not oneOf
                    self.assertNotIn(
                        'oneOf', request_schema,
                        f"{method.upper()} {path} should NOT have oneOf (array-only)"
                    )
                    self.assertEqual(
                        request_schema['type'], 'array',
                        f"{method.upper()} {path} should require array"
                    )
                    self.assertIn(
                        'items', request_schema,
                        f"{method.upper()} {path} array should have items"
                    )

    def test_bulk_delete_requires_array(self):
        """
        Bulk delete operations should require arrays.

        Refs: #20638
        """
        path = '/api/dcim/sites/'
        operation = self.schema['paths'][path]['delete']
        request_schema = operation['requestBody']['content']['application/json']['schema']

        # Should be array-only
        self.assertNotIn('oneOf', request_schema, "DELETE should NOT have oneOf")
        self.assertEqual(request_schema['type'], 'array', "DELETE should require array")
        self.assertIn('items', request_schema, "DELETE array should have items")

    def test_nested_related_fields_reference_brief_components(self):
        """
        A SerializedPKRelatedField declared with nested=True must reference the brief component in
        response schemas, as that is what the API returns.

        Refs: #22989
        """
        components = self.schema['components']['schemas']

        for component, field, ref in (
            ('Site', 'asns', 'BriefASN'),
            ('ConfigContext', 'sites', 'BriefSite'),
            ('Interface', 'tagged_vlans', 'BriefVLAN'),
        ):
            with self.subTest(component=component, field=field):
                self.assertEqual(
                    components[component]['properties'][field]['items']['$ref'],
                    f'#/components/schemas/{ref}'
                )

        # The brief component must advertise only the serializer's brief fields
        self.assertEqual(
            set(components['BriefASN']['properties']),
            {'id', 'url', 'display', 'asn', 'description'}
        )

    def test_ref_name_exempts_serializer_from_brief_prefix(self):
        """
        A serializer which declares an explicit Meta.ref_name keeps that name when nested, rather than
        acquiring a Brief prefix. These serializers are brief by design and have no complete form in the
        schema, so prefixing them would rename an existing component to no purpose.

        Refs: #22989
        """
        components = self.schema['components']['schemas']

        for component, field, ref in (
            ('ASN', 'sites', 'ASNSite'),
            ('ObjectPermission', 'groups', 'NestedGroup'),
            ('ObjectPermission', 'users', 'NestedUser'),
        ):
            with self.subTest(component=component, field=field):
                self.assertEqual(
                    components[component]['properties'][field]['items']['$ref'],
                    f'#/components/schemas/{ref}'
                )
                self.assertNotIn(f'Brief{ref}', components)

    def test_non_nested_related_fields_reference_full_components(self):
        """
        A SerializedPKRelatedField declared without nested=True must continue to reference the
        complete component.

        Refs: #22989
        """
        components = self.schema['components']['schemas']

        for field in ('import_targets', 'export_targets'):
            with self.subTest(field=field):
                self.assertEqual(
                    components['VRF']['properties'][field]['items']['$ref'],
                    '#/components/schemas/RouteTarget'
                )

    def test_nested_related_fields_accept_pks_on_write(self):
        """
        Request schemas for a SerializedPKRelatedField must continue to accept an array of integer
        primary keys.

        Refs: #22989
        """
        components = self.schema['components']['schemas']

        for component, field in (
            ('SiteRequest', 'asns'),
            ('ConfigContextRequest', 'sites'),
            ('ASNRequest', 'sites'),
        ):
            with self.subTest(component=component, field=field):
                self.assertEqual(components[component]['properties'][field]['items']['type'], 'integer')


class SerializedPKRelatedFieldSchemaTestCase(SimpleTestCase):
    """Tests for the schema extension which maps SerializedPKRelatedField."""

    class DummyComponent:
        ref = {'$ref': '#/components/schemas/Dummy'}

    class DummyAutoSchema:
        """Records the serializer resolved by the extension, in place of generating a component."""

        def __init__(self):
            self.resolved = []

        def resolve_serializer(self, serializer, direction):
            self.resolved.append(serializer)
            return SerializedPKRelatedFieldSchemaTestCase.DummyComponent

    def test_nested_flag_is_passed_to_serializer(self):
        """
        The field's serializer must be instantiated with the field's nested setting, so that the
        component matching the rendered representation is referenced.

        Refs: #22989
        """
        for nested in (True, False):
            with self.subTest(nested=nested):
                field = SerializedPKRelatedField(
                    serializer=SiteSerializer,
                    queryset=Site.objects.all(),
                    nested=nested
                )
                auto_schema = self.DummyAutoSchema()

                schema = FixSerializedPKRelatedField(field).map_serializer_field(auto_schema, 'response')

                serializer = auto_schema.resolved[0]
                self.assertIsInstance(serializer, SiteSerializer)
                self.assertEqual(serializer.nested, nested)
                self.assertEqual(schema, self.DummyComponent.ref)

    def test_request_schema_is_an_integer(self):
        """
        Request schemas must document an integer primary key, regardless of the nested setting.

        Refs: #22989
        """
        field = SerializedPKRelatedField(serializer=SiteSerializer, queryset=Site.objects.all(), nested=True)
        auto_schema = self.DummyAutoSchema()

        schema = FixSerializedPKRelatedField(field).map_serializer_field(auto_schema, 'request')

        self.assertEqual(schema['type'], 'integer')
        self.assertEqual(auto_schema.resolved, [])
