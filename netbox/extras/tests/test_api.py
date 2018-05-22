from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag

from dcim.models import Device
from extras.constants import GRAPH_TYPE_SITE
from extras.models import Graph, ExportTemplate
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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Graph.objects.count(), 4)
        graph4 = Graph.objects.get(pk=response.data['id'])
        self.assertEqual(graph4.type, data['type'])
        self.assertEqual(graph4.name, data['name'])
        self.assertEqual(graph4.source, data['source'])

    def test_create_graph_bulk(self):

        data = [
            {
                'type': GRAPH_TYPE_SITE,
                'name': 'Test Graph 4',
                'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=4',
            },
            {
                'type': GRAPH_TYPE_SITE,
                'name': 'Test Graph 5',
                'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=5',
            },
            {
                'type': GRAPH_TYPE_SITE,
                'name': 'Test Graph 6',
                'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=6',
            },
        ]

        url = reverse('extras-api:graph-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Graph.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_graph(self):

        data = {
            'type': GRAPH_TYPE_SITE,
            'name': 'Test Graph X',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=99',
        }

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.put(url, data, format='json', **self.header)

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


class ExportTemplateTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.content_type = ContentType.objects.get_for_model(Device)
        self.exporttemplate1 = ExportTemplate.objects.create(
            content_type=self.content_type, name='Test Export Template 1',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
        )
        self.exporttemplate2 = ExportTemplate.objects.create(
            content_type=self.content_type, name='Test Export Template 2',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
        )
        self.exporttemplate3 = ExportTemplate.objects.create(
            content_type=self.content_type, name='Test Export Template 3',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
        )

    def test_get_exporttemplate(self):

        url = reverse('extras-api:exporttemplate-detail', kwargs={'pk': self.exporttemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.exporttemplate1.name)

    def test_list_exporttemplates(self):

        url = reverse('extras-api:exporttemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_exporttemplate(self):

        data = {
            'content_type': self.content_type.pk,
            'name': 'Test Export Template 4',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        }

        url = reverse('extras-api:exporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ExportTemplate.objects.count(), 4)
        exporttemplate4 = ExportTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(exporttemplate4.content_type_id, data['content_type'])
        self.assertEqual(exporttemplate4.name, data['name'])
        self.assertEqual(exporttemplate4.template_code, data['template_code'])

    def test_create_exporttemplate_bulk(self):

        data = [
            {
                'content_type': self.content_type.pk,
                'name': 'Test Export Template 4',
                'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            },
            {
                'content_type': self.content_type.pk,
                'name': 'Test Export Template 5',
                'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            },
            {
                'content_type': self.content_type.pk,
                'name': 'Test Export Template 6',
                'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            },
        ]

        url = reverse('extras-api:exporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ExportTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_exporttemplate(self):

        data = {
            'content_type': self.content_type.pk,
            'name': 'Test Export Template X',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        }

        url = reverse('extras-api:exporttemplate-detail', kwargs={'pk': self.exporttemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ExportTemplate.objects.count(), 3)
        exporttemplate1 = ExportTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(exporttemplate1.name, data['name'])
        self.assertEqual(exporttemplate1.template_code, data['template_code'])

    def test_delete_exporttemplate(self):

        url = reverse('extras-api:exporttemplate-detail', kwargs={'pk': self.exporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExportTemplate.objects.count(), 2)


class TagTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.tag1 = Tag.objects.create(name='Test Tag 1', slug='test-tag-1')
        self.tag2 = Tag.objects.create(name='Test Tag 2', slug='test-tag-2')
        self.tag3 = Tag.objects.create(name='Test Tag 3', slug='test-tag-3')

    def test_get_tag(self):

        url = reverse('extras-api:tag-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.tag1.name)

    def test_list_tags(self):

        url = reverse('extras-api:tag-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_tag(self):

        data = {
            'name': 'Test Tag 4',
            'slug': 'test-tag-4',
        }

        url = reverse('extras-api:tag-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 4)
        tag4 = Tag.objects.get(pk=response.data['id'])
        self.assertEqual(tag4.name, data['name'])
        self.assertEqual(tag4.slug, data['slug'])

    def test_create_tag_bulk(self):

        data = [
            {
                'name': 'Test Tag 4',
                'slug': 'test-tag-4',
            },
            {
                'name': 'Test Tag 5',
                'slug': 'test-tag-5',
            },
            {
                'name': 'Test Tag 6',
                'slug': 'test-tag-6',
            },
        ]

        url = reverse('extras-api:tag-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_tag(self):

        data = {
            'name': 'Test Tag X',
            'slug': 'test-tag-x',
        }

        url = reverse('extras-api:tag-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Tag.objects.count(), 3)
        tag1 = Tag.objects.get(pk=response.data['id'])
        self.assertEqual(tag1.name, data['name'])
        self.assertEqual(tag1.slug, data['slug'])

    def test_delete_tag(self):

        url = reverse('extras-api:tag-detail', kwargs={'pk': self.tag1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 2)
