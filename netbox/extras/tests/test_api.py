import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status

from core.choices import ManagedFileRootPathChoices
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Rack, Location, RackRole, Site
from extras.choices import *
from extras.models import *
from extras.reports import Report
from extras.scripts import BooleanVar, IntegerVar, Script, StringVar
from utilities.testing import APITestCase, APIViewTestCases


User = get_user_model()


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
            'name': 'Webhook 4',
            'payload_url': 'http://example.com/?4',
        },
        {
            'name': 'Webhook 5',
            'payload_url': 'http://example.com/?5',
        },
        {
            'name': 'Webhook 6',
            'payload_url': 'http://example.com/?6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
        'ssl_verification': False,
    }

    @classmethod
    def setUpTestData(cls):

        webhooks = (
            Webhook(
                name='Webhook 1',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 2',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 3',
                payload_url='http://example.com/?1',
            ),
        )
        Webhook.objects.bulk_create(webhooks)


class EventRuleTest(APIViewTestCases.APIViewTestCase):
    model = EventRule
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'enabled': False,
        'description': 'New description',
    }
    update_data = {
        'name': 'Event Rule X',
        'enabled': False,
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        webhooks = (
            Webhook(
                name='Webhook 1',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 2',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 3',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 4',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 5',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 6',
                payload_url='http://example.com/?1',
            ),
        )
        Webhook.objects.bulk_create(webhooks)

        event_rules = (
            EventRule(name='EventRule 1', type_create=True, action_object=webhooks[0]),
            EventRule(name='EventRule 2', type_create=True, action_object=webhooks[1]),
            EventRule(name='EventRule 3', type_create=True, action_object=webhooks[2]),
        )
        EventRule.objects.bulk_create(event_rules)

        cls.create_data = [
            {
                'name': 'EventRule 4',
                'content_types': ['dcim.device', 'dcim.devicetype'],
                'type_create': True,
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[3].pk,
            },
            {
                'name': 'EventRule 5',
                'content_types': ['dcim.device', 'dcim.devicetype'],
                'type_create': True,
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[4].pk,
            },
            {
                'name': 'EventRule 6',
                'content_types': ['dcim.device', 'dcim.devicetype'],
                'type_create': True,
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[5].pk,
            },
        ]


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
            'type': 'text',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }
    update_data = {
        'content_types': ['dcim.device'],
        'name': 'New_Name',
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


class CustomFieldChoiceSetTest(APIViewTestCases.APIViewTestCase):
    model = CustomFieldChoiceSet
    brief_fields = ['choices_count', 'display', 'id', 'name', 'url']
    create_data = [
        {
            'name': 'Choice Set 4',
            'extra_choices': [
                ['4A', 'Choice 1'],
                ['4B', 'Choice 2'],
                ['4C', 'Choice 3'],
            ],
        },
        {
            'name': 'Choice Set 5',
            'extra_choices': [
                ['5A', 'Choice 1'],
                ['5B', 'Choice 2'],
                ['5C', 'Choice 3'],
            ],
        },
        {
            'name': 'Choice Set 6',
            'extra_choices': [
                ['6A', 'Choice 1'],
                ['6B', 'Choice 2'],
                ['6C', 'Choice 3'],
            ],
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }
    update_data = {
        'name': 'Choice Set X',
        'extra_choices': [
            ['X1', 'Choice 1'],
            ['X2', 'Choice 2'],
            ['X3', 'Choice 3'],
        ],
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        choice_sets = (
            CustomFieldChoiceSet(name='Choice Set 1', extra_choices=['1A', '1B', '1C', '1D', '1E']),
            CustomFieldChoiceSet(name='Choice Set 2', extra_choices=['2A', '2B', '2C', '2D', '2E']),
            CustomFieldChoiceSet(name='Choice Set 3', extra_choices=['3A', '3B', '3C', '3D', '3E']),
        )
        CustomFieldChoiceSet.objects.bulk_create(choice_sets)


class CustomLinkTest(APIViewTestCases.APIViewTestCase):
    model = CustomLink
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'content_types': ['dcim.site'],
            'name': 'Custom Link 4',
            'enabled': True,
            'link_text': 'Link 4',
            'link_url': 'http://example.com/?4',
        },
        {
            'content_types': ['dcim.site'],
            'name': 'Custom Link 5',
            'enabled': True,
            'link_text': 'Link 5',
            'link_url': 'http://example.com/?5',
        },
        {
            'content_types': ['dcim.site'],
            'name': 'Custom Link 6',
            'enabled': False,
            'link_text': 'Link 6',
            'link_url': 'http://example.com/?6',
        },
    ]
    bulk_update_data = {
        'new_window': True,
        'enabled': False,
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        custom_links = (
            CustomLink(
                name='Custom Link 1',
                enabled=True,
                link_text='Link 1',
                link_url='http://example.com/?1',
            ),
            CustomLink(
                name='Custom Link 2',
                enabled=True,
                link_text='Link 2',
                link_url='http://example.com/?2',
            ),
            CustomLink(
                name='Custom Link 3',
                enabled=False,
                link_text='Link 3',
                link_url='http://example.com/?3',
            ),
        )
        CustomLink.objects.bulk_create(custom_links)
        for i, custom_link in enumerate(custom_links):
            custom_link.content_types.set([site_ct])


class SavedFilterTest(APIViewTestCases.APIViewTestCase):
    model = SavedFilter
    brief_fields = ['display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'content_types': ['dcim.site'],
            'name': 'Saved Filter 4',
            'slug': 'saved-filter-4',
            'weight': 100,
            'enabled': True,
            'shared': True,
            'parameters': {'status': ['active']},
        },
        {
            'content_types': ['dcim.site'],
            'name': 'Saved Filter 5',
            'slug': 'saved-filter-5',
            'weight': 200,
            'enabled': True,
            'shared': True,
            'parameters': {'status': ['planned']},
        },
        {
            'content_types': ['dcim.site'],
            'name': 'Saved Filter 6',
            'slug': 'saved-filter-6',
            'weight': 300,
            'enabled': True,
            'shared': True,
            'parameters': {'status': ['retired']},
        },
    ]
    bulk_update_data = {
        'weight': 1000,
        'enabled': False,
        'shared': False,
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        saved_filters = (
            SavedFilter(
                name='Saved Filter 1',
                slug='saved-filter-1',
                weight=100,
                enabled=True,
                shared=True,
                parameters={'status': ['active']}
            ),
            SavedFilter(
                name='Saved Filter 2',
                slug='saved-filter-2',
                weight=200,
                enabled=True,
                shared=True,
                parameters={'status': ['planned']}
            ),
            SavedFilter(
                name='Saved Filter 3',
                slug='saved-filter-3',
                weight=300,
                enabled=True,
                shared=True,
                parameters={'status': ['retired']}
            ),
        )
        SavedFilter.objects.bulk_create(saved_filters)
        for i, savedfilter in enumerate(saved_filters):
            savedfilter.content_types.set([site_ct])


class BookmarkTest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase
):
    model = Bookmark
    brief_fields = ['display', 'id', 'object_id', 'object_type', 'url']

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
            Site(name='Site 4', slug='site-4'),
            Site(name='Site 5', slug='site-5'),
            Site(name='Site 6', slug='site-6'),
        )
        Site.objects.bulk_create(sites)

    def setUp(self):
        super().setUp()

        sites = Site.objects.all()

        bookmarks = (
            Bookmark(object=sites[0], user=self.user),
            Bookmark(object=sites[1], user=self.user),
            Bookmark(object=sites[2], user=self.user),
        )
        Bookmark.objects.bulk_create(bookmarks)

        self.create_data = [
            {
                'object_type': 'dcim.site',
                'object_id': sites[3].pk,
                'user': self.user.pk,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[4].pk,
                'user': self.user.pk,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[5].pk,
                'user': self.user.pk,
            },
        ]


class ExportTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ExportTemplate
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'content_types': ['dcim.device'],
            'name': 'Test Export Template 4',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        },
        {
            'content_types': ['dcim.device'],
            'name': 'Test Export Template 5',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        },
        {
            'content_types': ['dcim.device'],
            'name': 'Test Export Template 6',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        export_templates = (
            ExportTemplate(
                name='Export Template 1',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
            ExportTemplate(
                name='Export Template 2',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
            ExportTemplate(
                name='Export Template 3',
                template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}'
            ),
        )
        ExportTemplate.objects.bulk_create(export_templates)
        for et in export_templates:
            et.content_types.set([ContentType.objects.get_for_model(Device)])


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
    APIViewTestCases.DeleteObjectViewTestCase,
    APIViewTestCases.GraphQLTestCase
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


class JournalEntryTest(APIViewTestCases.APIViewTestCase):
    model = JournalEntry
    brief_fields = ['created', 'display', 'id', 'url']
    bulk_update_data = {
        'comments': 'Overwritten',
    }

    @classmethod
    def setUpTestData(cls):
        user = User.objects.first()
        site = Site.objects.create(name='Site 1', slug='site-1')

        journal_entries = (
            JournalEntry(
                created_by=user,
                assigned_object=site,
                comments='Fourth entry',
            ),
            JournalEntry(
                created_by=user,
                assigned_object=site,
                comments='Fifth entry',
            ),
            JournalEntry(
                created_by=user,
                assigned_object=site,
                comments='Sixth entry',
            ),
        )
        JournalEntry.objects.bulk_create(journal_entries)

        cls.create_data = [
            {
                'assigned_object_type': 'dcim.site',
                'assigned_object_id': site.pk,
                'comments': 'First entry',
            },
            {
                'assigned_object_type': 'dcim.site',
                'assigned_object_id': site.pk,
                'comments': 'Second entry',
            },
            {
                'assigned_object_type': 'dcim.site',
                'assigned_object_id': site.pk,
                'comments': 'Third entry',
            },
        ]


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
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        site = Site.objects.create(name='Site-1', slug='site-1')
        device = Device.objects.create(name='Device 1', device_type=devicetype, role=role, site=site)

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


class ConfigTemplateTest(APIViewTestCases.APIViewTestCase):
    model = ConfigTemplate
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'name': 'Config Template 4',
            'template_code': 'Foo: {{ foo }}',
        },
        {
            'name': 'Config Template 5',
            'template_code': 'Bar: {{ bar }}',
        },
        {
            'name': 'Config Template 6',
            'template_code': 'Baz: {{ baz }}',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        config_templates = (
            ConfigTemplate(
                name='Config Template 1',
                template_code='Foo: {{ foo }}'
            ),
            ConfigTemplate(
                name='Config Template 2',
                template_code='Bar: {{ bar }}'
            ),
            ConfigTemplate(
                name='Config Template 3',
                template_code='Baz: {{ baz }}'
            ),
        )
        ConfigTemplate.objects.bulk_create(config_templates)


class ReportTest(APITestCase):

    class TestReport(Report):

        def test_foo(self):
            self.log_success(None, "Report completed")

    @classmethod
    def setUpTestData(cls):
        ReportModule.objects.create(
            file_root=ManagedFileRootPathChoices.REPORTS,
            file_path='/var/tmp/report.py'
        )

    def get_test_report(self, *args):
        return ReportModule.objects.first(), self.TestReport()

    def setUp(self):
        super().setUp()

        # Monkey-patch the API viewset's _get_report() method to return our test Report above
        from extras.api.views import ReportViewSet
        ReportViewSet._get_report = self.get_test_report

    def test_get_report(self):
        url = reverse('extras-api:report-detail', kwargs={'pk': None})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.TestReport.__name__)


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

    @classmethod
    def setUpTestData(cls):
        ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path='/var/tmp/script.py'
        )

    def get_test_script(self, *args):
        return ScriptModule.objects.first(), self.TestScript

    def setUp(self):
        super().setUp()

        # Monkey-patch the API viewset's _get_script() method to return our test Script above
        from extras.api.views import ScriptViewSet
        ScriptViewSet._get_script = self.get_test_script

    def test_get_script(self):

        url = reverse('extras-api:script-detail', kwargs={'pk': None})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.TestScript.Meta.name)
        self.assertEqual(response.data['vars']['var1'], 'StringVar')
        self.assertEqual(response.data['vars']['var2'], 'IntegerVar')
        self.assertEqual(response.data['vars']['var3'], 'BooleanVar')


class CreatedUpdatedFilterTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        site1 = Site.objects.create(name='Site 1', slug='site-1')
        location1 = Location.objects.create(site=site1, name='Location 1', slug='location-1')
        rackrole1 = RackRole.objects.create(name='Rack Role 1', slug='rack-role-1', color='ff0000')
        racks = (
            Rack(site=site1, location=location1, role=rackrole1, name='Rack 1', u_height=42),
            Rack(site=site1, location=location1, role=rackrole1, name='Rack 2', u_height=42)
        )
        Rack.objects.bulk_create(racks)

        # Change the created and last_updated of the second rack
        Rack.objects.filter(pk=racks[1].pk).update(
            last_updated=make_aware(datetime.datetime(2001, 2, 3, 1, 2, 3, 4)),
            created=make_aware(datetime.datetime(2001, 2, 3))
        )

    def test_get_rack_created(self):
        rack2 = Rack.objects.get(name='Rack 2')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created=2001-02-03'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack2.pk)

    def test_get_rack_created_gte(self):
        rack1 = Rack.objects.get(name='Rack 1')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__gte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack1.pk)

    def test_get_rack_created_lte(self):
        rack2 = Rack.objects.get(name='Rack 2')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?created__lte=2001-02-04'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack2.pk)

    def test_get_rack_last_updated(self):
        rack2 = Rack.objects.get(name='Rack 2')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated=2001-02-03%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack2.pk)

    def test_get_rack_last_updated_gte(self):
        rack1 = Rack.objects.get(name='Rack 1')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__gte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack1.pk)

    def test_get_rack_last_updated_lte(self):
        rack2 = Rack.objects.get(name='Rack 2')
        self.add_permissions('dcim.view_rack')
        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?last_updated__lte=2001-02-04%2001:02:03.000004'.format(url), **self.header)

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], rack2.pk)


class ContentTypeTest(APITestCase):

    def test_list_objects(self):
        contenttype_count = ContentType.objects.count()

        response = self.client.get(reverse('extras-api:contenttype-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], contenttype_count)

    def test_get_object(self):
        contenttype = ContentType.objects.first()

        url = reverse('extras-api:contenttype-detail', kwargs={'pk': contenttype.pk})
        self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_200_OK)
