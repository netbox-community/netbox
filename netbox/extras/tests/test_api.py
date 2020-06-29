import datetime

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Rack, RackGroup, RackRole, Site
from extras.api.views import ScriptViewSet
from extras.models import ConfigContext, Graph, ExportTemplate, Tag
from extras.scripts import BooleanVar, IntegerVar, Script, StringVar
from utilities.testing import APITestCase, APIViewTestCases
from utilities.utils import copy_safe_request


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('extras-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class GraphTest(APIViewTestCases.APIViewTestCase):
    model = Graph
    brief_fields = ['id', 'name', 'url']
    create_data = [
        {
            'type': 'dcim.site',
            'name': 'Graph 4',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=4',
        },
        {
            'type': 'dcim.site',
            'name': 'Graph 5',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=5',
        },
        {
            'type': 'dcim.site',
            'name': 'Graph 6',
            'source': 'http://example.com/graphs.py?site={{ obj.name }}&foo=6',
        },
    ]

    @classmethod
    def setUpTestData(cls):
        ct = ContentType.objects.get_for_model(Site)

        graphs = (
            Graph(type=ct, name='Graph 1', source='http://example.com/graphs.py?site={{ obj.name }}&foo=1'),
            Graph(type=ct, name='Graph 2', source='http://example.com/graphs.py?site={{ obj.name }}&foo=2'),
            Graph(type=ct, name='Graph 3', source='http://example.com/graphs.py?site={{ obj.name }}&foo=3'),
        )
        Graph.objects.bulk_create(graphs)


class ExportTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ExportTemplate
    brief_fields = ['id', 'name', 'url']
    create_data = [
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

    @classmethod
    def setUpTestData(cls):
        ct = ContentType.objects.get_for_model(Device)

        export_templates = (
            ExportTemplate(
                content_type=ct,
                name='Export Template 1',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
            ExportTemplate(
                content_type=ct,
                name='Export Template 2',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
            ExportTemplate(
                content_type=ct,
                name='Export Template 3',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
        )
        ExportTemplate.objects.bulk_create(export_templates)


class TagTest(APIViewTestCases.APIViewTestCase):
    model = Tag
    brief_fields = ['color', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Tag 4',
            'slug': 'tag-4',
        },
        {
            'name': 'Tag 5',
            'slug': 'tag-5',
        },
        {
            'name': 'Tag 6',
            'slug': 'tag-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)


class ConfigContextTest(APIViewTestCases.APIViewTestCase):
    model = ConfigContext
    brief_fields = ['id', 'name', 'url']
    create_data = [
        {
            'name': 'Config Context 4',
            'data': {'more_foo': True},
        },
        {
            'name': 'Config Context 5',
            'data': {'more_bar': False},
        },
        {
            'name': 'Config Context 6',
            'data': {'more_baz': None},
        },
    ]

    @classmethod
    def setUpTestData(cls):

        config_contexts = (
            ConfigContext(name='Config Context 1', weight=100, data={'foo': 123}),
            ConfigContext(name='Config Context 2', weight=200, data={'bar': 456}),
            ConfigContext(name='Config Context 3', weight=300, data={'baz': 789}),
        )
        ConfigContext.objects.bulk_create(config_contexts)

    def test_render_configcontext_for_object(self):
        """
        Test rendering config context data for a device.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        site = Site.objects.create(name='Site-1', slug='site-1')
        device = Device.objects.create(name='Device 1', device_type=devicetype, device_role=devicerole, site=site)

        # Test default config contexts (created at test setup)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['foo'], 123)
        self.assertEqual(rendered_context['bar'], 456)
        self.assertEqual(rendered_context['baz'], 789)

        # Add another context specific to the site
        configcontext4 = ConfigContext(
            name='Config Context 4',
            data={'site_data': 'ABC'}
        )
        configcontext4.save()
        configcontext4.sites.add(site)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['site_data'], 'ABC')

        # Override one of the default contexts
        configcontext5 = ConfigContext(
            name='Config Context 5',
            weight=2000,
            data={'foo': 999}
        )
        configcontext5.save()
        configcontext5.sites.add(site)
        rendered_context = device.get_config_context()
        self.assertEqual(rendered_context['foo'], 999)

        # Add a context which does NOT match our device and ensure it does not apply
        site2 = Site.objects.create(name='Site 2', slug='site-2')
        configcontext6 = ConfigContext(
            name='Config Context 6',
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

        def run(self, data, commit=True):

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

        self.assertEqual(response.data['result']['status']['value'], 'pending')


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
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created=2001-02-03'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_created_gte(self):
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__gte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack1.pk)

    def test_get_rack_created_lte(self):
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__lte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_last_updated(self):
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated=2001-02-03%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)

    def test_get_rack_last_updated_gte(self):
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__gte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack1.pk)

    def test_get_rack_last_updated_lte(self):
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__lte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.rack2.pk)
