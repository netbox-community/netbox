from django.test import override_settings
from django.urls import reverse

from utilities.testing import disable_warnings, TestCase


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
