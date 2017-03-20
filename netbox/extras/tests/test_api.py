from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.urls import reverse

from extras.models import Graph, GRAPH_TYPE_SITE
from users.models import Token
from utilities.tests import HttpStatusMixin


class GraphTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.graph1 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 1', source='http://example.com/graphs.py?site={{ obj.name }}&foo=1'
        )
        self.graph2 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 2', source='http://example.com/graphs.py?site={{ obj.name }}&foo=2'
        )
        self.graph3 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 3', source='http://example.com/graphs.py?site={{ obj.name }}&foo=3'
        )

    def test_get_graph(self):

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.graph1.name)

    def test_list_graphs(self):

        url = reverse('extras-api:graph-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_graph(self):

        data = {
            'type': GRAPH_TYPE_SITE,
            'name': 'Test Graph 4',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=4',
        }

        url = reverse('extras-api:graph-list')
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Graph.objects.count(), 4)
        graph4 = Graph.objects.get(pk=response.data['id'])
        self.assertEqual(graph4.type, data['type'])
        self.assertEqual(graph4.name, data['name'])
        self.assertEqual(graph4.source, data['source'])

    def test_update_graph(self):

        data = {
            'type': GRAPH_TYPE_SITE,
            'name': 'Test Graph X',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=99',
        }

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Graph.objects.count(), 3)
        graph1 = Graph.objects.get(pk=response.data['id'])
        self.assertEqual(graph1.type, data['type'])
        self.assertEqual(graph1.name, data['name'])
        self.assertEqual(graph1.source, data['source'])

    def test_delete_graph(self):

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Graph.objects.count(), 2)
