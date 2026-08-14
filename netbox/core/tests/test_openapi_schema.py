"""
Unit tests for OpenAPI schema generation.

Refs: #20638
"""
import json

from django.test import TestCase


class OpenAPISchemaTestCase(TestCase):
    """Tests for OpenAPI schema generation."""

    def setUp(self):
        """Fetch schema via API endpoint."""
        response = self.client.get('/api/schema/', {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        self.schema = json.loads(response.content)

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
