import datetime

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status

from core.choices import ManagedFileRootPathChoices
from core.events import *
from core.models import ObjectType
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Rack, Location, RackRole, Site
from extras.choices import *
from extras.models import *
from extras.scripts import BooleanVar, IntegerVar, Script as PythonClass, StringVar
from users.models import Group, User
from utilities.testing import APITestCase, APIViewTestCases


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('extras-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class WebhookTest(APIViewTestCases.APIViewTestCase):
    model = Webhook
    brief_fields = ['description', 'display', 'id', 'name', 'url']
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
    brief_fields = ['description', 'display', 'id', 'name', 'url']
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
            EventRule(name='EventRule 1', event_types=[OBJECT_CREATED], action_object=webhooks[0]),
            EventRule(name='EventRule 2', event_types=[OBJECT_CREATED], action_object=webhooks[1]),
            EventRule(name='EventRule 3', event_types=[OBJECT_CREATED], action_object=webhooks[2]),
        )
        EventRule.objects.bulk_create(event_rules)

        cls.create_data = [
            {
                'name': 'EventRule 4',
                'object_types': ['dcim.device', 'dcim.devicetype'],
                'event_types': [OBJECT_CREATED],
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[3].pk,
            },
            {
                'name': 'EventRule 5',
                'object_types': ['dcim.device', 'dcim.devicetype'],
                'event_types': [OBJECT_CREATED],
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[4].pk,
            },
            {
                'name': 'EventRule 6',
                'object_types': ['dcim.device', 'dcim.devicetype'],
                'event_types': [OBJECT_CREATED],
                'action_type': EventRuleActionChoices.WEBHOOK,
                'action_object_type': 'extras.webhook',
                'action_object_id': webhooks[5].pk,
            },
        ]


class CustomFieldTest(APIViewTestCases.APIViewTestCase):
    model = CustomField
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    create_data = [
        {
            'object_types': ['dcim.site'],
            'name': 'cf4',
            'type': 'date',
        },
        {
            'object_types': ['dcim.site'],
            'name': 'cf5',
            'type': 'url',
        },
        {
            'object_types': ['dcim.site'],
            'name': 'cf6',
            'type': 'text',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }
    update_data = {
        'object_types': ['dcim.device'],
        'name': 'New_Name',
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        site_ct = ObjectType.objects.get_for_model(Site)

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
            cf.object_types.add(site_ct)


class CustomFieldChoiceSetTest(APIViewTestCases.APIViewTestCase):
    model = CustomFieldChoiceSet
    brief_fields = ['choices_count', 'description', 'display', 'id', 'name', 'url']
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
            CustomFieldChoiceSet(
                name='Choice Set 1',
                extra_choices=[['1A', '1A'], ['1B', '1B'], ['1C', '1C'], ['1D', '1D'], ['1E', '1E']],
            ),
            CustomFieldChoiceSet(
                name='Choice Set 2',
                extra_choices=[['2A', '2A'], ['2B', '2B'], ['2C', '2C'], ['2D', '2D'], ['2E', '2E']],
            ),
            CustomFieldChoiceSet(
                name='Choice Set 3',
                extra_choices=[['3A', '3A'], ['3B', '3B'], ['3C', '3C'], ['3D', '3D'], ['3E', '3E']],
            ),
        )
        CustomFieldChoiceSet.objects.bulk_create(choice_sets)

    def test_invalid_choice_items(self):
        """
        Attempting to define each choice as a single-item list should return a 400 error.
        """
        self.add_permissions('extras.add_customfieldchoiceset')
        data = {
            "name": "test",
            "extra_choices": [
                ["choice1"],
                ["choice2"],
                ["choice3"],
            ]
        }

        response = self.client.post(self._get_list_url(), data, format='json', **self.header)
        self.assertEqual(response.status_code, 400)


class CustomLinkTest(APIViewTestCases.APIViewTestCase):
    model = CustomLink
    brief_fields = ['display', 'id', 'name', 'url']
    create_data = [
        {
            'object_types': ['dcim.site'],
            'name': 'Custom Link 4',
            'enabled': True,
            'link_text': 'Link 4',
            'link_url': 'http://example.com/?4',
        },
        {
            'object_types': ['dcim.site'],
            'name': 'Custom Link 5',
            'enabled': True,
            'link_text': 'Link 5',
            'link_url': 'http://example.com/?5',
        },
        {
            'object_types': ['dcim.site'],
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
        site_type = ObjectType.objects.get_for_model(Site)

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
            custom_link.object_types.set([site_type])


class SavedFilterTest(APIViewTestCases.APIViewTestCase):
    model = SavedFilter
    brief_fields = ['description', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'object_types': ['dcim.site'],
            'name': 'Saved Filter 4',
            'slug': 'saved-filter-4',
            'weight': 100,
            'enabled': True,
            'shared': True,
            'parameters': {'status': ['active']},
        },
        {
            'object_types': ['dcim.site'],
            'name': 'Saved Filter 5',
            'slug': 'saved-filter-5',
            'weight': 200,
            'enabled': True,
            'shared': True,
            'parameters': {'status': ['planned']},
        },
        {
            'object_types': ['dcim.site'],
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
        site_type = ObjectType.objects.get_for_model(Site)

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
            savedfilter.object_types.set([site_type])


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
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    create_data = [
        {
            'object_types': ['dcim.device'],
            'name': 'Test Export Template 4',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        },
        {
            'object_types': ['dcim.device'],
            'name': 'Test Export Template 5',
            'template_code': '{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
        },
        {
            'object_types': ['dcim.device'],
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
            et.object_types.set([ObjectType.objects.get_for_model(Device)])


class TagTest(APIViewTestCases.APIViewTestCase):
    model = Tag
    brief_fields = ['color', 'description', 'display', 'id', 'name', 'slug', 'url']
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
                object_type=ct,
                object_id=site.pk,
                name='Image Attachment 1',
                image='http://example.com/image1.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                object_type=ct,
                object_id=site.pk,
                name='Image Attachment 2',
                image='http://example.com/image2.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                object_type=ct,
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
    brief_fields = ['description', 'display', 'id', 'name', 'url']
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
    brief_fields = ['description', 'display', 'id', 'name', 'url']
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


class ScriptTest(APITestCase):

    class TestScriptClass(PythonClass):

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
        module = ScriptModule.objects.create(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path='/var/tmp/script.py'
        )
        Script.objects.create(
            module=module,
            name="Test script",
            is_executable=True,
        )

    def python_class(self):
        return self.TestScriptClass

    def setUp(self):
        super().setUp()

        # Monkey-patch the Script model to return our TestScriptClass above
        Script.python_class = self.python_class

    def test_get_script(self):
        module = ScriptModule.objects.get(
            file_root=ManagedFileRootPathChoices.SCRIPTS,
            file_path='/var/tmp/script.py'
        )
        script = module.scripts.all().first()
        url = reverse('extras-api:script-detail', kwargs={'pk': script.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.TestScriptClass.Meta.name)
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


class ObjectTypeTest(APITestCase):

    def test_list_objects(self):
        object_type_count = ObjectType.objects.count()

        response = self.client.get(reverse('extras-api:objecttype-list'), **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], object_type_count)

    def test_get_object(self):
        object_type = ObjectType.objects.first()

        url = reverse('extras-api:objecttype-detail', kwargs={'pk': object_type.pk})
        self.assertHttpStatus(self.client.get(url, **self.header), status.HTTP_200_OK)


class SubscriptionTest(APIViewTestCases.APIViewTestCase):
    model = Subscription
    brief_fields = ['display', 'id', 'object_id', 'object_type', 'url', 'user']

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
            User(username='User 4'),
        )
        User.objects.bulk_create(users)
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        subscriptions = (
            Subscription(
                object=sites[0],
                user=users[0],
            ),
            Subscription(
                object=sites[1],
                user=users[1],
            ),
            Subscription(
                object=sites[2],
                user=users[2],
            ),
        )
        Subscription.objects.bulk_create(subscriptions)

        cls.create_data = [
            {
                'object_type': 'dcim.site',
                'object_id': sites[0].pk,
                'user': users[3].pk,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[1].pk,
                'user': users[3].pk,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[2].pk,
                'user': users[3].pk,
            },
        ]


class NotificationGroupTest(APIViewTestCases.APIViewTestCase):
    model = NotificationGroup
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    create_data = [
        {
            'object_types': ['dcim.site'],
            'name': 'Custom Link 4',
            'enabled': True,
            'link_text': 'Link 4',
            'link_url': 'http://example.com/?4',
        },
        {
            'object_types': ['dcim.site'],
            'name': 'Custom Link 5',
            'enabled': True,
            'link_text': 'Link 5',
            'link_url': 'http://example.com/?5',
        },
        {
            'object_types': ['dcim.site'],
            'name': 'Custom Link 6',
            'enabled': False,
            'link_text': 'Link 6',
            'link_url': 'http://example.com/?6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)
        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        notification_groups = (
            NotificationGroup(name='Notification Group 1'),
            NotificationGroup(name='Notification Group 2'),
            NotificationGroup(name='Notification Group 3'),
        )
        NotificationGroup.objects.bulk_create(notification_groups)
        for i, notification_group in enumerate(notification_groups):
            notification_group.users.add(users[i])
            notification_group.groups.add(groups[i])

        cls.create_data = [
            {
                'name': 'Notification Group 4',
                'description': 'Foo',
                'users': [users[0].pk],
                'groups': [groups[0].pk],
            },
            {
                'name': 'Notification Group 5',
                'description': 'Bar',
                'users': [users[1].pk],
                'groups': [groups[1].pk],
            },
            {
                'name': 'Notification Group 6',
                'description': 'Baz',
                'users': [users[2].pk],
                'groups': [groups[2].pk],
            },
        ]


class NotificationTest(APIViewTestCases.APIViewTestCase):
    model = Notification
    brief_fields = ['display', 'event_type', 'id', 'object_id', 'object_type', 'read', 'url', 'user']

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
            User(username='User 4'),
        )
        User.objects.bulk_create(users)
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        notifications = (
            Notification(
                object=sites[0],
                event_type=OBJECT_CREATED,
                user=users[0],
            ),
            Notification(
                object=sites[1],
                event_type=OBJECT_UPDATED,
                user=users[1],
            ),
            Notification(
                object=sites[2],
                event_type=OBJECT_DELETED,
                user=users[2],
            ),
        )
        Notification.objects.bulk_create(notifications)

        cls.create_data = [
            {
                'object_type': 'dcim.site',
                'object_id': sites[0].pk,
                'user': users[3].pk,
                'event_type': OBJECT_CREATED,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[1].pk,
                'user': users[3].pk,
                'event_type': OBJECT_UPDATED,
            },
            {
                'object_type': 'dcim.site',
                'object_id': sites[2].pk,
                'user': users[3].pk,
                'event_type': OBJECT_DELETED,
            },
        ]
