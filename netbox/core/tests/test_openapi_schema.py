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
