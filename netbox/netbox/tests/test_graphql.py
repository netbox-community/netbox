import json

from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from rest_framework import status
from users.models import ObjectPermission, Token
from users.models import User
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
        from dcim.models import Site, Location

        site = Site.objects.create(name='Site A', slug='site-a')
        location = Location.objects.create(site=site, name='Location A1', slug='location-a1')

        url = reverse('graphql')
        field_name = 'location_list'
        query = '{location_list(filters: {site_id: "' + str(site.id) + '"}) {id site {id}}}'

        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Location))

        response = self.client.post(url, data={'query': query}, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        self.assertGreater(len(data['data']['location_list']), 0)

        query = '{location_list(filters: {site_id: "' + str(site.id + 1234) + '"}) {id site {id}}}'
        response = self.client.post(url, data={'query': query}, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']['location_list']), 0)
