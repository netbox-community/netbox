import datetime
from unittest import skipIf

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import make_aware
from django_rq.queues import get_connection
from rest_framework import status
from rq import Worker

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Rack, Location, RackRole, Site
from extras.api.views import ReportViewSet, ScriptViewSet
from extras.models import *
from extras.reports import Report
from extras.scripts import BooleanVar, IntegerVar, Script, StringVar
from utilities.testing import APITestCase, APIViewTestCases


rq_worker_running = Worker.count(get_connection('default'))


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('extras-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class WebhookTest(APIViewTestCases.APIViewTestCase):
    model = Webhook
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'content_types': ['dcim.device', 'dcim.devicetype'],
            'name': 'Webhook 4',
            'type_create': True,
            'payload_url': 'http://example.com/?4',
        },
        {
            'content_types': ['dcim.device', 'dcim.devicetype'],
            'name': 'Webhook 5',
            'type_update': True,
            'payload_url': 'http://example.com/?5',
        },
        {
            'content_types': ['dcim.device', 'dcim.devicetype'],
            'name': 'Webhook 6',
            'type_delete': True,
            'payload_url': 'http://example.com/?6',
        },
    ]
    bulk_update_data = {
        'ssl_verification': False,
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)
        rack_ct = ContentType.objects.get_for_model(Rack)

        webhooks = (
            Webhook(
                name='Webhook 1',
                type_create=True,
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 2',
                type_update=True,
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 3',
                type_delete=True,
                payload_url='http://example.com/?1',
            ),
        )
        Webhook.objects.bulk_create(webhooks)
        for webhook in webhooks:
            webhook.content_types.add(site_ct, rack_ct)


class CustomFieldTest(APIViewTestCases.APIViewTestCase):
    model = CustomField
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'content_types': ['dcim.site'],
            'name': 'cf4',
            'type': 'date',
        },
        {
            'content_types': ['dcim.site'],
            'name': 'cf5',
            'type': 'url',
        },
        {
            'content_types': ['dcim.site'],
            'name': 'cf6',
            'type': 'select',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        custom_fields = (
            CustomField(
                name='cf1',
                type='text'
            ),
            CustomField(
                name='cf2',
                type='integer'
            ),
            CustomField(
                name='cf3',
                type='boolean'
            ),
        )
        CustomField.objects.bulk_create(custom_fields)
        for cf in custom_fields:
            cf.content_types.add(site_ct)


class CustomLinkTest(APIViewTestCases.APIViewTestCase):
    model = CustomLink
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'content_type': 'dcim.site',
            'name': 'Custom Link 4',
            'link_text': 'Link 4',
            'link_url': 'http://example.com/?4',
        },
        {
            'content_type': 'dcim.site',
            'name': 'Custom Link 5',
            'link_text': 'Link 5',
            'link_url': 'http://example.com/?5',
        },
        {
            'content_type': 'dcim.site',
            'name': 'Custom Link 6',
            'link_text': 'Link 6',
            'link_url': 'http://example.com/?6',
        },
    ]
    bulk_update_data = {
        'new_window': True,
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        custom_links = (
            CustomLink(
                content_type=site_ct,
                name='Custom Link 1',
                link_text='Link 1',
                link_url='http://example.com/?1',
            ),
            CustomLink(
                content_type=site_ct,
                name='Custom Link 2',
                link_text='Link 2',
                link_url='http://example.com/?2',
            ),
            CustomLink(
                content_type=site_ct,
                name='Custom Link 3',
                link_text='Link 3',
                link_url='http://example.com/?3',
            ),
        )
        CustomLink.objects.bulk_create(custom_links)


class ExportTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ExportTemplate
    brief_fields = ['display', 'id', 'name', 'url']
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
    bulk_update_data = {
        'description': 'New description',
    }

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
    brief_fields = ['color', 'display', 'id', 'name', 'slug', 'url']
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
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)


# TODO: Standardize to APIViewTestCase (needs create & update tests)
class ImageAttachmentTest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase
):
    model = ImageAttachment
    brief_fields = ['display', 'id', 'image', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        ct = ContentType.objects.get_for_model(Site)

        site = Site.objects.create(name='Site 1', slug='site-1')

        image_attachments = (
            ImageAttachment(
                content_type=ct,
                object_id=site.pk,
                name='Image Attachment 1',
                image='http://example.com/image1.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                content_type=ct,
                object_id=site.pk,
                name='Image Attachment 2',
                image='http://example.com/image2.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                content_type=ct,
                object_id=site.pk,
                name='Image Attachment 3',
                image='http://example.com/image3.png',
                image_height=100,
                image_width=100
            )
        )
        ImageAttachment.objects.bulk_create(image_attachments)


class ConfigContextTest(APIViewTestCases.APIViewTestCase):
    model = ConfigContext
    brief_fields = ['display', 'id', 'name', 'url']
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
    bulk_update_data = {
        'description': 'New description',
    }

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


class ReportTest(APITestCase):

    class TestReport(Report):

        def test_foo(self):
            self.log_success(None, "Report completed")

    def get_test_report(self, *args):
        return self.TestReport()

    def setUp(self):
        super().setUp()

        # Monkey-patch the API viewset's _get_script method to return our test script above
        ReportViewSet._retrieve_report = self.get_test_report

    def test_get_report(self):
        url = reverse('extras-api:report-detail', kwargs={'pk': None})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.TestReport.__name__)

    @skipIf(not rq_worker_running, "RQ worker not running")
    def test_run_report(self):
        self.add_permissions('extras.run_script')

        url = reverse('extras-api:report-run', kwargs={'pk': None})
        response = self.client.post(url, {}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(response.data['result']['status']['value'], 'pending')


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

    @skipIf(not rq_worker_running, "RQ worker not running")
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
        self.location1 = Location.objects.create(site=self.site1, name='Test Location 1', slug='test-location-1')
        self.rackrole1 = RackRole.objects.create(name='Test Rack Role 1', slug='test-rack-role-1', color='ff0000')
        self.rack1 = Rack.objects.create(
            site=self.site1, location=self.location1, role=self.rackrole1, name='Test Rack 1', u_height=42,
        )
        self.rack2 = Rack.objects.create(
            site=self.site1, location=self.location1, role=self.rackrole1, name='Test Rack 2', u_height=42,
        )

        # change the created and last_updated of one
        Rack.objects.filter(pk=self.rack2.pk).update(
            last_updated=make_aware(datetime.datetime(2001, 2, 3, 1, 2, 3, 4)),
            created=make_aware(datetime.datetime(2001, 2, 3))
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


class ContentTypeTest(APITestCase):

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['contenttypes.contenttype'])
    def test_list_objects(self):
        contenttype_count = ContentType.objects.count()

        response = self.client.get(reverse('extras-api:contenttype-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], contenttype_count)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['contenttypes.contenttype'])
    def test_get_object(self):
        contenttype = ContentType.objects.first()

        url = reverse('extras-api:contenttype-detail', kwargs={'pk': contenttype.pk})
        self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_200_OK)
