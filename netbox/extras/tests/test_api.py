from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from taggit.models import Tag

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Region, Site
from extras.constants import GRAPH_TYPE_SITE
from extras.models import ConfigContext, Graph, ExportTemplate
from tenancy.models import Tenant, TenantGroup
from utilities.testing import APITestCase


class GraphTest(APITestCase):

    def setUp(self):

        super(GraphTest, self).setUp()

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


class ExportTemplateTest(APITestCase):

    def setUp(self):

        super(ExportTemplateTest, self).setUp()

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


class TagTest(APITestCase):

    def setUp(self):

        super(TagTest, self).setUp()

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


class ConfigContextTest(APITestCase):

    def setUp(self):

        super(ConfigContextTest, self).setUp()

        self.configcontext1 = ConfigContext.objects.create(
            name='Test Config Context 1',
            weight=100,
            data={'foo': 123}
        )
        self.configcontext2 = ConfigContext.objects.create(
            name='Test Config Context 2',
            weight=200,
            data={'bar': 456}
        )
        self.configcontext3 = ConfigContext.objects.create(
            name='Test Config Context 3',
            weight=300,
            data={'baz': 789}
        )

    def test_get_configcontext(self):

        url = reverse('extras-api:configcontext-detail', kwargs={'pk': self.configcontext1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.configcontext1.name)
        self.assertEqual(response.data['data'], self.configcontext1.data)

    def test_list_configcontexts(self):

        url = reverse('extras-api:configcontext-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_configcontext(self):

        region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        role1 = DeviceRole.objects.create(name='Test Role 1', slug='test-role-1')
        role2 = DeviceRole.objects.create(name='Test Role 2', slug='test-role-2')
        platform1 = Platform.objects.create(name='Test Platform 1', slug='test-platform-1')
        platform2 = Platform.objects.create(name='Test Platform 2', slug='test-platform-2')
        tenantgroup1 = TenantGroup.objects.create(name='Test Tenant Group 1', slug='test-tenant-group-1')
        tenantgroup2 = TenantGroup.objects.create(name='Test Tenant Group 2', slug='test-tenant-group-2')
        tenant1 = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1')
        tenant2 = Tenant.objects.create(name='Test Tenant 2', slug='test-tenant-2')

        data = {
            'name': 'Test Config Context 4',
            'weight': 1000,
            'regions': [region1.pk, region2.pk],
            'sites': [site1.pk, site2.pk],
            'roles': [role1.pk, role2.pk],
            'platforms': [platform1.pk, platform2.pk],
            'tenant_groups': [tenantgroup1.pk, tenantgroup2.pk],
            'tenants': [tenant1.pk, tenant2.pk],
            'data': {'foo': 'XXX'}
        }

        url = reverse('extras-api:configcontext-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConfigContext.objects.count(), 4)
        configcontext4 = ConfigContext.objects.get(pk=response.data['id'])
        self.assertEqual(configcontext4.name, data['name'])
        self.assertEqual(region1.pk, data['regions'][0])
        self.assertEqual(region2.pk, data['regions'][1])
        self.assertEqual(site1.pk, data['sites'][0])
        self.assertEqual(site2.pk, data['sites'][1])
        self.assertEqual(role1.pk, data['roles'][0])
        self.assertEqual(role2.pk, data['roles'][1])
        self.assertEqual(platform1.pk, data['platforms'][0])
        self.assertEqual(platform2.pk, data['platforms'][1])
        self.assertEqual(tenantgroup1.pk, data['tenant_groups'][0])
        self.assertEqual(tenantgroup2.pk, data['tenant_groups'][1])
        self.assertEqual(tenant1.pk, data['tenants'][0])
        self.assertEqual(tenant2.pk, data['tenants'][1])
        self.assertEqual(configcontext4.data, data['data'])

    def test_create_configcontext_bulk(self):

        data = [
            {
                'name': 'Test Config Context 4',
                'data': {'more_foo': True},
            },
            {
                'name': 'Test Config Context 5',
                'data': {'more_bar': False},
            },
            {
                'name': 'Test Config Context 6',
                'data': {'more_baz': None},
            },
        ]

        url = reverse('extras-api:configcontext-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConfigContext.objects.count(), 6)
        for i in range(0, 3):
            self.assertEqual(response.data[i]['name'], data[i]['name'])
            self.assertEqual(response.data[i]['data'], data[i]['data'])

    def test_update_configcontext(self):

        region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')

        data = {
            'name': 'Test Config Context X',
            'weight': 999,
            'regions': [region1.pk, region2.pk],
            'data': {'foo': 'XXX'}
        }

        url = reverse('extras-api:configcontext-detail', kwargs={'pk': self.configcontext1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ConfigContext.objects.count(), 3)
        configcontext1 = ConfigContext.objects.get(pk=response.data['id'])
        self.assertEqual(configcontext1.name, data['name'])
        self.assertEqual(configcontext1.weight, data['weight'])
        self.assertEqual(sorted([r.pk for r in configcontext1.regions.all()]), sorted(data['regions']))
        self.assertEqual(configcontext1.data, data['data'])

    def test_delete_configcontext(self):

        url = reverse('extras-api:configcontext-detail', kwargs={'pk': self.configcontext1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConfigContext.objects.count(), 2)

    def test_render_configcontext_for_object(self):

        # Create a Device for which we'll render a config context
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            slug='test-manufacturer'
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Test Device Type'
        )
        device_role = DeviceRole.objects.create(
            name='Test Role',
            slug='test-role'
        )
        site = Site.objects.create(
            name='Test Site',
            slug='test-site'
        )
        device = Device.objects.create(
            name='Test Device',
            device_type=device_type,
            device_role=device_role,
            site=site
        )

        # Test default config contexts (created at test setup)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['foo'], 123)
        self.assertEqual(rendered_context['bar'], 456)
        self.assertEqual(rendered_context['baz'], 789)

        # Add another context specific to the site
        configcontext4 = ConfigContext(
            name='Test Config Context 4',
            data={'site_data': 'ABC'}
        )
        configcontext4.save()
        configcontext4.sites.add(site)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['site_data'], 'ABC')

        # Override one of the default contexts
        configcontext5 = ConfigContext(
            name='Test Config Context 5',
            weight=2000,
            data={'foo': 999}
        )
        configcontext5.save()
        configcontext5.sites.add(site)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['foo'], 999)

        # Add a context which does NOT match our device and ensure it does not apply
        site2 = Site.objects.create(
            name='Test Site 2',
            slug='test-site-2'
        )
        configcontext6 = ConfigContext(
            name='Test Config Context 6',
            weight=2000,
            data={'bar': 999}
        )
        configcontext6.save()
        configcontext6.sites.add(site2)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['bar'], 456)
