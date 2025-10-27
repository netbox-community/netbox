import json

import strawberry
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from strawberry.types.lazy_type import LazyType

from core.models import ObjectType
from dcim.choices import LocationStatusChoices
from dcim.models import Site, Location
from netbox.graphql.schema import QueryV1, QueryV2
from users.models import ObjectPermission
from utilities.testing import disable_warnings, APITestCase, TestCase


class GraphQLTestCase(TestCase):

    @override_settings(GRAPHQL_ENABLED=False)
    def test_graphql_enabled(self):
        """
        The /graphql URL should return a 404 when GRAPHQL_ENABLED=False
        """
        url = reverse('graphql')
        response = self.client.get(url)
        self.assertHttpStatus(response, 404)

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


class GraphQLAPITestCase(APITestCase):

    def test_versioned_types(self):
        """
        Check that the GraphQL types defined for each version of the schema (V1 and V2) are correct.
        """
        schemas = (
            (1, QueryV1),
            (2, QueryV2),
        )

        def _get_class_name(field):
            try:
                if type(field.type) is strawberry.types.base.StrawberryList:
                    # Skip scalars
                    if field.type.of_type in (str, int):
                        return
                    if type(field.type.of_type) is LazyType:
                        return field.type.of_type.type_name
                    return field.type.of_type.__name__
                if hasattr(field.type, 'name'):
                    return field.type.__name__
            except AttributeError:
                # Unknown field type
                return

        def _check_version(class_name, version):
            if version == 1:
                self.assertTrue(class_name.endswith('V1'), f"{class_name} (v1) is not a V1 type")
            elif version == 2:
                self.assertFalse(class_name.endswith('V1'), f"{class_name} (v2) is a V1 type")

        for version, query in schemas:
            schema = strawberry.Schema(query=query)
            query_type = schema.get_type_by_name(query.__name__)

            # Iterate through root fields
            for field in query_type.fields:
                # Check for V1 suffix on class names
                if type_class := _get_class_name(field):
                    _check_version(type_class, version)

                    # Iterate through nested fields
                    subquery_type = schema.get_type_by_name(type_class)
                    for subfield in subquery_type.fields:
                        # Check for V1 suffix on class names
                        if type_class := _get_class_name(subfield):
                            _check_version(type_class, version)

    @override_settings(LOGIN_REQUIRED=True)
    def test_graphql_filter_objects(self):
        """
        Test the operation of filters for GraphQL API requests.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
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

        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Location))
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Site))

        url = reverse('graphql')

        # A valid request should return the filtered list
        query = '{location_list(filters: {site_id: "' + str(sites[0].pk) + '"}) {id site {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['location_list']), 1)
        self.assertIsNotNone(data['data']['location_list'][0]['site'])

        # Test OR logic
        query = """{
            location_list( filters: {
                status: STATUS_PLANNED,
                OR: {status: STATUS_STAGING}
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
        obj_perm.object_types.remove(ObjectType.objects.get_for_model(Location))
        query = '{site(id: ' + str(sites[0].pk) + ') {id locations {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['site']['locations']), 0)
