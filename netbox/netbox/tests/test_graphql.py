import json

from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from core.models import ObjectType
from dcim.models import Site, Location
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

    @override_settings(LOGIN_REQUIRED=True)
    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*', 'auth.user'])
    def test_graphql_filter_objects(self):
        """
        Test the operation of filters for GraphQL API requests.
        """
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)
        Location.objects.create(site=sites[0], name='Location 1', slug='location-1'),
        Location.objects.create(site=sites[1], name='Location 2', slug='location-2'),

        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Location))

        # A valid request should return the filtered list
        url = reverse('graphql')
        query = '{location_list(filters: {site_id: "' + str(sites[0].pk) + '"}) {id site {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertEqual(len(data['data']['location_list']), 1)

        # An invalid request should return an empty list
        query = '{location_list(filters: {site_id: "99999"}) {id site {id}}}'  # Invalid site ID
        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['location_list']), 0)
