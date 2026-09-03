"""
Unit tests for OpenAPI schema generation.

Refs: #20638
"""
import json

from django.test import SimpleTestCase, TestCase, override_settings

from core.api.schema import FixSerializedPKRelatedField, NetBoxAutoSchema
from dcim.api.serializers import SiteSerializer
from dcim.models import Site
from ipam.api.serializers import ServiceSerializer
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import BulkOperationErrorSerializer


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
})
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

    def _get_response_schema(self, path, method, code):
        """Return the JSON response schema documented for the given operation and status code."""
        responses = self.schema['paths'][path][method]['responses']
        self.assertIn(code, responses, f"{method.upper()} {path} should document a {code} response")
        return responses[code]['content']['application/json']['schema']

    def test_bulk_error_component_is_defined(self):
        """
        The structured error body returned by a failed bulk operation should be a named component,
        so that generated clients have a type for it.

        Refs: #20054
        """
        components = self.schema['components']['schemas']

        self.assertIn('BulkOperationError', components)
        envelope = components['BulkOperationError']
        self.assertEqual(sorted(envelope['properties']), ['detail', 'errors'])
        # `errors` is absent where the request could not be attributed to individual entries
        self.assertEqual(envelope['required'], ['detail'])
        self.assertEqual(
            envelope['properties']['errors']['items']['$ref'],
            '#/components/schemas/BulkOperationEntryError',
        )

        self.assertIn('BulkOperationEntryError', components)
        entry = components['BulkOperationEntryError']
        # An entry is correlated by `id` or by `index`, so neither is required; `errors` always is
        self.assertEqual(sorted(entry['properties']), ['errors', 'id', 'index'])
        self.assertEqual(entry['required'], ['errors'])

    def test_bulk_update_documents_error_response(self):
        """
        Bulk update operations should document the structured 400 response.

        Refs: #20054
        """
        ref = {'$ref': '#/components/schemas/BulkOperationError'}

        for path in ('/api/dcim/sites/', '/api/ipam/prefixes/', '/api/users/users/'):
            for method in ('put', 'patch'):
                with self.subTest(path=path, method=method):
                    self.assertEqual(self._get_response_schema(path, method, '400'), ref)

    def test_bulk_delete_documents_error_responses(self):
        """
        Bulk delete operations should document the 400 (unresolvable request or protection rule), the
        403 (not permitted) and the 409 (dependent object) responses.

        Refs: #20054
        """
        ref = {'$ref': '#/components/schemas/BulkOperationError'}

        for path in ('/api/dcim/sites/', '/api/ipam/prefixes/', '/api/users/users/'):
            with self.subTest(path=path):
                self.assertEqual(self._get_response_schema(path, 'delete', '400'), ref)
                self.assertEqual(self._get_response_schema(path, 'delete', '403'), ref)
                self.assertEqual(self._get_response_schema(path, 'delete', '409'), ref)

    def test_bulk_write_operations_document_forbidden_response(self):
        """
        Every bulk write should document the 403 returned when an object-level permission refuses one
        of the objects specified.

        Refs: #20054
        """
        ref = {'$ref': '#/components/schemas/BulkOperationError'}

        for path in ('/api/dcim/sites/', '/api/ipam/prefixes/', '/api/users/users/'):
            for method in ('post', 'put', 'patch', 'delete'):
                with self.subTest(path=path, method=method):
                    self.assertEqual(self._get_response_schema(path, method, '403'), ref)

    def test_create_documents_error_response_for_either_shape(self):
        """
        A POST to a list endpoint accepts either a single object or a list, so its 400 response
        should document both the field-keyed and the bulk error shapes.

        Refs: #20054
        """
        for path in ('/api/dcim/sites/', '/api/ipam/prefixes/', '/api/users/users/'):
            with self.subTest(path=path):
                schema = self._get_response_schema(path, 'post', '400')
                self.assertEqual(
                    schema['oneOf'],
                    [
                        {'type': 'object', 'additionalProperties': {}},
                        {'$ref': '#/components/schemas/BulkOperationError'},
                    ],
                )

    def test_detail_operations_omit_bulk_error_response(self):
        """
        The bulk error body applies only to list endpoints; detail endpoints must not advertise it.

        Refs: #20054
        """
        path = '/api/dcim/sites/{id}/'

        for method in ('get', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                responses = self.schema['paths'][path][method]['responses']
                self.assertNotIn('409', responses)
                self.assertNotIn('403', responses)
                for code, response in responses.items():
                    schema = response.get('content', {}).get('application/json', {}).get('schema', {})
                    self.assertNotEqual(
                        schema.get('$ref'), '#/components/schemas/BulkOperationError',
                        f"{method.upper()} {path} ({code}) should not reference the bulk error body"
                    )

    def test_service_request_documents_legacy_protocol_and_ports(self):
        """
        The deprecated protocol/ports pair remains writable on application services (the serializer
        translates it into port_mappings), so both must appear in the request body alongside
        port_mappings. protocol is backed by a read-only model property rather than a model field,
        which previously caused it to be dropped from the generated writable variant.

        Refs: #20285
        """
        for path in ('/api/ipam/services/', '/api/ipam/service-templates/'):
            with self.subTest(path=path):
                schema = self.schema['paths'][path]['post']['requestBody']['content']['application/json']['schema']
                ref = schema['oneOf'][0]['$ref'].split('/')[-1]
                properties = self.schema['components']['schemas'][ref]['properties']

                for field in ('port_mappings', 'protocol', 'ports'):
                    self.assertIn(field, properties, f"{ref} should document the '{field}' field")

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

    def test_script_run_operation_exists(self):
        """
        Encodes presence of extras_scripts_run operation in schema as expected.

        Refs: #22569
        """
        paths = self.schema['paths']
        resource_path = paths['/api/extras/scripts/{id}/']
        self.assertIn('post', resource_path)

        run_operation = resource_path['post']

        self.assertEqual(run_operation['operationId'], 'extras_scripts_run')
        self.assertEqual(len(run_operation['responses']), 1)
        self.assertIn('200', run_operation['responses'])


class WritableFieldRebuildTestCase(TestCase):
    """
    Tests for NetBoxAutoSchema._rebuilds_as_writable(), which decides whether a declared
    ChoiceField/WritableNestedSerializer can be nulled out on the generated writable variant and
    left for DRF to rebuild from the model. Getting this wrong drops the field from the request
    body silently, so the predicate must match DRF's own build_field() behavior rather than merely
    testing the model for a field of that name.

    Refs: #23083
    """

    def test_rebuildable_fields(self):
        """Fields DRF can rebuild writably should be reported as such."""
        serializer = ServiceSerializer()

        for field_name in ('name', 'description', 'ipaddresses'):
            with self.subTest(field_name=field_name):
                self.assertTrue(NetBoxAutoSchema._rebuilds_as_writable(serializer, field_name))

    def test_non_rebuildable_fields(self):
        """
        Fields DRF rebuilds as read-only (or cannot rebuild at all) must be reported as not
        rebuildable, so that the declared field is retained instead.
        """
        serializer = ServiceSerializer()
        cases = {
            'protocol': "backed by a read-only model property, not a model field",
            'parent': "a GenericForeignKey, absent from DRF's field info",
            'created': "a non-editable model field",
            'no_such_field': "not present on the model at all",
        }

        for field_name, reason in cases.items():
            with self.subTest(field_name=field_name):
                self.assertFalse(
                    NetBoxAutoSchema._rebuilds_as_writable(serializer, field_name),
                    f"'{field_name}' should not be considered rebuildable ({reason})"
                )

    def test_serializer_without_model(self):
        """A serializer with no Meta.model has nothing to rebuild from."""
        self.assertFalse(NetBoxAutoSchema._rebuilds_as_writable(BulkOperationErrorSerializer(), 'id'))


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
