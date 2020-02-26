import datetime

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Platform, Rack, RackGroup, RackRole, Region, Site
from extras.api.views import ScriptViewSet
from extras.choices import *
from extras.constants import GRAPH_MODELS
from extras.models import ConfigContext, Graph, ExportTemplate, Tag
from extras.scripts import BooleanVar, IntegerVar, Script, StringVar
from tenancy.models import Tenant, TenantGroup
from utilities.testing import APITestCase, choices_to_dict


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('extras-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)

    def test_choices(self):

        url = reverse('extras-api:field-choice-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, 200)

        # ExportTemplate
        self.assertEqual(choices_to_dict(response.data.get('export-template:template_language')), TemplateLanguageChoices.as_dict())

        # Graph
        content_types = ContentType.objects.filter(GRAPH_MODELS)
        graph_type_choices = {
            "{}.{}".format(ct.app_label, ct.model): ct.name for ct in content_types
        }
        self.assertEqual(choices_to_dict(response.data.get('graph:type')), graph_type_choices)
        self.assertEqual(choices_to_dict(response.data.get('graph:template_language')), TemplateLanguageChoices.as_dict())

        # ObjectChange
        self.assertEqual(choices_to_dict(response.data.get('object-change:action')), ObjectChangeActionChoices.as_dict())


class GraphTest(APITestCase):

    def setUp(self):

        super().setUp()

        site_ct = ContentType.objects.get_for_model(Site)
        self.graph1 = Graph.objects.create(
            type=site_ct,
            name='Test Graph 1',
            source='http://example.com/graphs.py?site={{ obj.name }}&foo=1'
        )
        self.graph2 = Graph.objects.create(
            type=site_ct,
            name='Test Graph 2',
            source='http://example.com/graphs.py?site={{ obj.name }}&foo=2'
        )
        self.graph3 = Graph.objects.create(
            type=site_ct,
            name='Test Graph 3',
            source='http://example.com/graphs.py?site={{ obj.name }}&foo=3'
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
            'type': 'dcim.site',
            'name': 'Test Graph 4',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=4',
        }

        url = reverse('extras-api:graph-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Graph.objects.count(), 4)
        graph4 = Graph.objects.get(pk=response.data['id'])
        self.assertEqual(graph4.type, ContentType.objects.get_for_model(Site))
        self.assertEqual(graph4.name, data['name'])
        self.assertEqual(graph4.source, data['source'])

    def test_create_graph_bulk(self):

        data = [
            {
                'type': 'dcim.site',
                'name': 'Test Graph 4',
                'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=4',
            },
            {
                'type': 'dcim.site',
                'name': 'Test Graph 5',
                'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=5',
            },
            {
                'type': 'dcim.site',
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
            'type': 'dcim.site',
            'name': 'Test Graph X',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=99',
        }

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Graph.objects.count(), 3)
        graph1 = Graph.objects.get(pk=response.data['id'])
        self.assertEqual(graph1.type, ContentType.objects.get_for_model(Site))
        self.assertEqual(graph1.name, data['name'])
        self.assertEqual(graph1.source, data['source'])

    def test_delete_graph(self):

        url = reverse('extras-api:graph-detail', kwargs={'pk': self.graph1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Graph.objects.count(), 2)


class ExportTemplateTest(APITestCase):

    def setUp(self):

        super().setUp()

        content_type = ContentType.objects.get_for_model(Device)
        self.exporttemplate1 = ExportTemplate.objects.create(
            content_type=content_type, name='Test Export Template 1',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
        )
        self.exporttemplate2 = ExportTemplate.objects.create(
            content_type=content_type, name='Test Export Template 2',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
        )
        self.exporttemplate3 = ExportTemplate.objects.create(
            content_type=content_type, name='Test Export Template 3',
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
            'content_type': 'dcim.device',
            'name': 'Test Export Template 4',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        }

        url = reverse('extras-api:exporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ExportTemplate.objects.count(), 4)
        exporttemplate4 = ExportTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(exporttemplate4.content_type, ContentType.objects.get_for_model(Device))
        self.assertEqual(exporttemplate4.name, data['name'])
        self.assertEqual(exporttemplate4.template_code, data['template_code'])

    def test_create_exporttemplate_bulk(self):

        data = [
            {
                'content_type': 'dcim.device',
                'name': 'Test Export Template 4',
                'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            },
            {
                'content_type': 'dcim.device',
                'name': 'Test Export Template 5',
                'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            },
            {
                'content_type': 'dcim.device',
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
            'content_type': 'dcim.device',
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

        super().setUp()

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

        super().setUp()

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
        tag1 = Tag.objects.create(name='Test Tag 1', slug='test-tag-1')
        tag2 = Tag.objects.create(name='Test Tag 2', slug='test-tag-2')

        data = {
            'name': 'Test Config Context 4',
            'weight': 1000,
            'regions': [region1.pk, region2.pk],
            'sites': [site1.pk, site2.pk],
            'roles': [role1.pk, role2.pk],
            'platforms': [platform1.pk, platform2.pk],
            'tenant_groups': [tenantgroup1.pk, tenantgroup2.pk],
            'tenants': [tenant1.pk, tenant2.pk],
            'tags': [tag1.slug, tag2.slug],
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
        self.assertEqual(tag1.slug, data['tags'][0])
        self.assertEqual(tag2.slug, data['tags'][1])
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


class ScriptTest(APITestCase):

    class TestScript(Script):

        class Meta:
            name = "Test script"

        var1 = StringVar()
        var2 = IntegerVar()
        var3 = BooleanVar()

        def run(self, data):

            self.log_info(data['var1'])
            self.log_success(data['var2'])
            self.log_failure(data['var3'])

            return 'Script complete'

    def get_test_script(self, *args):
        return self.TestScript

    def setUp(self):

        super().setUp()

        # Monkey-patch the API viewset's _get_script method to return our test script above
        ScriptViewSet._get_script = self.get_test_script

    def test_get_script(self):

        url = reverse('extras-api:script-detail', kwargs={'pk': None})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.TestScript.Meta.name)
        self.assertEqual(response.data['vars']['var1'], 'StringVar')
        self.assertEqual(response.data['vars']['var2'], 'IntegerVar')
        self.assertEqual(response.data['vars']['var3'], 'BooleanVar')

    def test_run_script(self):

        script_data = {
            'var1': 'FooBar',
            'var2': 123,
            'var3': False,
        }

        data = {
            'data': script_data,
            'commit': True,
        }

        url = reverse('extras-api:script-detail', kwargs={'pk': None})
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(response.data['log'][0]['status'], 'info')
        self.assertEqual(response.data['log'][0]['message'], script_data['var1'])
        self.assertEqual(response.data['log'][1]['status'], 'success')
        self.assertEqual(response.data['log'][1]['message'], script_data['var2'])
        self.assertEqual(response.data['log'][2]['status'], 'failure')
        self.assertEqual(response.data['log'][2]['message'], script_data['var3'])
        self.assertEqual(response.data['output'], 'Script complete')


class CreatedUpdatedFilterTest(APITestCase):

    def setUp(self):

        super().setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.rackgroup1 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 1', slug='test-rack-group-1')
        self.rackrole1 = RackRole.objects.create(name='Test Rack Role 1', slug='test-rack-role-1', color='ff0000')
        self.rack1 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 1', u_height=42,
        )
        self.rack2 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 2', u_height=42,
        )

        # change the created and last_updated of one
        Rack.objects.filter(pk=self.rack2.pk).update(
            last_updated=datetime.datetime(2001, 2, 3, 1, 2, 3, 4, tzinfo=timezone.utc),
            created=datetime.datetime(2001, 2, 3)
        )

    def test_get_rack_created(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created=2001-02-03'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_created_gte(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__gte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack1.pk)

    def test_get_rack_created_lte(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__lte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_last_updated(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated=2001-02-03%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_last_updated_gte(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__gte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack1.pk)

    def test_get_rack_last_updated_lte(self):
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__lte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)
