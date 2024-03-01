import urllib.parse
import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer, Site
from extras.choices import *
from extras.models import *
from utilities.testing import ViewTestCases, TestCase

User = get_user_model()


class CustomFieldTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CustomField

    @classmethod
    def setUpTestData(cls):

        site_type = ObjectType.objects.get_for_model(Site)
        CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            extra_choices=(
                ('A', 'A'),
                ('B', 'B'),
                ('C', 'C'),
            )
        )

        custom_fields = (
            CustomField(name='field1', label='Field 1', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='field2', label='Field 2', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='field3', label='Field 3', type=CustomFieldTypeChoices.TYPE_TEXT),
        )
        for customfield in custom_fields:
            customfield.save()
            customfield.object_types.add(site_type)

        cls.form_data = {
            'name': 'field_x',
            'label': 'Field X',
            'type': 'text',
            'object_types': [site_type.pk],
            'search_weight': 2000,
            'filter_logic': CustomFieldFilterLogicChoices.FILTER_EXACT,
            'default': None,
            'weight': 200,
            'required': True,
            'ui_visible': CustomFieldUIVisibleChoices.ALWAYS,
            'ui_editable': CustomFieldUIEditableChoices.YES,
        }

        cls.csv_data = (
            'name,label,type,object_types,object_type,weight,search_weight,filter_logic,choice_set,validation_minimum,validation_maximum,validation_regex,ui_visible,ui_editable',
            'field4,Field 4,text,dcim.site,,100,1000,exact,,,,[a-z]{3},always,yes',
            'field5,Field 5,integer,dcim.site,,100,2000,exact,,1,100,,always,yes',
            'field6,Field 6,select,dcim.site,,100,3000,exact,Choice Set 1,,,,always,yes',
            'field7,Field 7,object,dcim.site,dcim.region,100,4000,exact,,,,,always,yes',
        )

        cls.csv_update_data = (
            'id,label',
            f'{custom_fields[0].pk},New label 1',
            f'{custom_fields[1].pk},New label 2',
            f'{custom_fields[2].pk},New label 3',
        )

        cls.bulk_edit_data = {
            'required': True,
            'weight': 200,
        }


class CustomFieldChoiceSetTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CustomFieldChoiceSet

    @classmethod
    def setUpTestData(cls):

        choice_sets = (
            CustomFieldChoiceSet(
                name='Choice Set 1',
                extra_choices=(('A1', 'Choice 1'), ('A2', 'Choice 2'), ('A3', 'Choice 3'))
            ),
            CustomFieldChoiceSet(
                name='Choice Set 2',
                extra_choices=(('B1', 'Choice 1'), ('B2', 'Choice 2'), ('B3', 'Choice 3'))
            ),
            CustomFieldChoiceSet(
                name='Choice Set 3',
                extra_choices=(('C1', 'Choice 1'), ('C2', 'Choice 2'), ('C3', 'Choice 3'))
            ),
            CustomFieldChoiceSet(
                name='Choice Set 4',
                extra_choices=(('D1', 'Choice 1'), ('D2', 'Choice 2'), ('D3', 'Choice 3'))
            ),
        )
        CustomFieldChoiceSet.objects.bulk_create(choice_sets)

        cls.form_data = {
            'name': 'Choice Set X',
            'extra_choices': '\n'.join(['X1:Choice 1', 'X2:Choice 2', 'X3:Choice 3'])
        }

        cls.csv_data = (
            'name,extra_choices',
            'Choice Set 5,"D1,D2,D3"',
            'Choice Set 6,"E1,E2,E3"',
            'Choice Set 7,"F1,F2,F3"',
            'Choice Set 8,"F1:L1,F2:L2,F3:L3"',
        )

        cls.csv_update_data = (
            'id,extra_choices',
            f'{choice_sets[0].pk},"A,B,C"',
            f'{choice_sets[1].pk},"A,B,C"',
            f'{choice_sets[2].pk},"A,B,C"',
            f'{choice_sets[3].pk},"A:L1,B:L2,C:L3"',
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }

    # This is here as extra_choices field splits on colon, but is returned
    # from DB as comma separated.
    def assertInstanceEqual(self, instance, data, exclude=None, api=False):
        if 'extra_choices' in data:
            data['extra_choices'] = data['extra_choices'].replace(':', ',')
        return super().assertInstanceEqual(instance, data, exclude, api)


class CustomLinkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CustomLink

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)
        custom_links = (
            CustomLink(name='Custom Link 1', enabled=True, link_text='Link 1', link_url='http://example.com/?1'),
            CustomLink(name='Custom Link 2', enabled=True, link_text='Link 2', link_url='http://example.com/?2'),
            CustomLink(name='Custom Link 3', enabled=False, link_text='Link 3', link_url='http://example.com/?3'),
        )
        CustomLink.objects.bulk_create(custom_links)
        for i, custom_link in enumerate(custom_links):
            custom_link.object_types.set([site_type])

        cls.form_data = {
            'name': 'Custom Link X',
            'object_types': [site_type.pk],
            'enabled': False,
            'weight': 100,
            'button_class': CustomLinkButtonClassChoices.DEFAULT,
            'link_text': 'Link X',
            'link_url': 'http://example.com/?x'
        }

        cls.csv_data = (
            "name,object_types,enabled,weight,button_class,link_text,link_url",
            "Custom Link 4,dcim.site,True,100,blue,Link 4,http://exmaple.com/?4",
            "Custom Link 5,dcim.site,True,100,blue,Link 5,http://exmaple.com/?5",
            "Custom Link 6,dcim.site,False,100,blue,Link 6,http://exmaple.com/?6",
        )

        cls.csv_update_data = (
            "id,name",
            f"{custom_links[0].pk},Custom Link 7",
            f"{custom_links[1].pk},Custom Link 8",
            f"{custom_links[2].pk},Custom Link 9",
        )

        cls.bulk_edit_data = {
            'button_class': CustomLinkButtonClassChoices.CYAN,
            'enabled': False,
            'weight': 200,
        }


class SavedFilterTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = SavedFilter

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        saved_filters = (
            SavedFilter(
                name='Saved Filter 1',
                slug='saved-filter-1',
                user=users[0],
                weight=100,
                parameters={'status': ['active']}
            ),
            SavedFilter(
                name='Saved Filter 2',
                slug='saved-filter-2',
                user=users[1],
                weight=200,
                parameters={'status': ['planned']}
            ),
            SavedFilter(
                name='Saved Filter 3',
                slug='saved-filter-3',
                user=users[2],
                weight=300,
                parameters={'status': ['retired']}
            ),
        )
        SavedFilter.objects.bulk_create(saved_filters)
        for i, savedfilter in enumerate(saved_filters):
            savedfilter.content_types.set([site_ct])

        cls.form_data = {
            'name': 'Saved Filter X',
            'slug': 'saved-filter-x',
            'content_types': [site_ct.pk],
            'description': 'Foo',
            'weight': 1000,
            'enabled': True,
            'shared': True,
            'parameters': '{"foo": 123}',
        }

        cls.csv_data = (
            'name,slug,content_types,weight,enabled,shared,parameters',
            'Saved Filter 4,saved-filter-4,dcim.device,400,True,True,{"foo": "a"}',
            'Saved Filter 5,saved-filter-5,dcim.device,500,True,True,{"foo": "b"}',
            'Saved Filter 6,saved-filter-6,dcim.device,600,True,True,{"foo": "c"}',
        )

        cls.csv_update_data = (
            "id,name",
            f"{saved_filters[0].pk},Saved Filter 7",
            f"{saved_filters[1].pk},Saved Filter 8",
            f"{saved_filters[2].pk},Saved Filter 9",
        )

        cls.bulk_edit_data = {
            'weight': 999,
        }


class BookmarkTestCase(
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = Bookmark

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
            Site(name='Site 4', slug='site-4'),
        )
        Site.objects.bulk_create(sites)

        cls.form_data = {
            'object_type': site_ct.pk,
            'object_id': sites[3].pk,
        }

    def setUp(self):
        super().setUp()

        sites = Site.objects.all()
        user = self.user

        bookmarks = (
            Bookmark(object=sites[0], user=user),
            Bookmark(object=sites[1], user=user),
            Bookmark(object=sites[2], user=user),
        )
        Bookmark.objects.bulk_create(bookmarks)

    def _get_url(self, action, instance=None):
        if action == 'list':
            return reverse('account:bookmarks')
        return super()._get_url(action, instance)

    def test_list_objects_anonymous(self):
        return

    def test_list_objects_with_constrained_permission(self):
        return


class ExportTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ExportTemplate

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)
        TEMPLATE_CODE = """{% for object in queryset %}{{ object }}{% endfor %}"""

        export_templates = (
            ExportTemplate(name='Export Template 1', template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 2', template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 3', template_code=TEMPLATE_CODE),
        )
        ExportTemplate.objects.bulk_create(export_templates)
        for et in export_templates:
            et.object_types.set([site_type])

        cls.form_data = {
            'name': 'Export Template X',
            'object_types': [site_type.pk],
            'template_code': TEMPLATE_CODE,
        }

        cls.csv_data = (
            "name,object_types,template_code",
            f"Export Template 4,dcim.site,{TEMPLATE_CODE}",
            f"Export Template 5,dcim.site,{TEMPLATE_CODE}",
            f"Export Template 6,dcim.site,{TEMPLATE_CODE}",
        )

        cls.csv_update_data = (
            "id,name",
            f"{export_templates[0].pk},Export Template 7",
            f"{export_templates[1].pk},Export Template 8",
            f"{export_templates[2].pk},Export Template 9",
        )

        cls.bulk_edit_data = {
            'mime_type': 'text/html',
            'file_extension': 'html',
            'as_attachment': True,
        }


class WebhookTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Webhook

    @classmethod
    def setUpTestData(cls):

        webhooks = (
            Webhook(name='Webhook 1', payload_url='http://example.com/?1', http_method='POST'),
            Webhook(name='Webhook 2', payload_url='http://example.com/?2', http_method='POST'),
            Webhook(name='Webhook 3', payload_url='http://example.com/?3', http_method='POST'),
        )
        for webhook in webhooks:
            webhook.save()

        cls.form_data = {
            'name': 'Webhook X',
            'payload_url': 'http://example.com/?x',
            'http_method': 'GET',
            'http_content_type': 'application/foo',
            'description': 'My webhook',
        }

        cls.csv_data = (
            "name,payload_url,http_method,http_content_type,description",
            "Webhook 4,http://example.com/?4,GET,application/json,Foo",
            "Webhook 5,http://example.com/?5,GET,application/json,Bar",
            "Webhook 6,http://example.com/?6,GET,application/json,Baz",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{webhooks[0].pk},Webhook 7,Foo",
            f"{webhooks[1].pk},Webhook 8,Bar",
            f"{webhooks[2].pk},Webhook 9,Baz",
        )

        cls.bulk_edit_data = {
            'http_method': 'GET',
        }


class EventRulesTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = EventRule

    @classmethod
    def setUpTestData(cls):

        webhooks = (
            Webhook(name='Webhook 1', payload_url='http://example.com/?1', http_method='POST'),
            Webhook(name='Webhook 2', payload_url='http://example.com/?2', http_method='POST'),
            Webhook(name='Webhook 3', payload_url='http://example.com/?3', http_method='POST'),
        )
        for webhook in webhooks:
            webhook.save()

        site_type = ObjectType.objects.get_for_model(Site)
        event_rules = (
            EventRule(name='EventRule 1', type_create=True, action_object=webhooks[0]),
            EventRule(name='EventRule 2', type_create=True, action_object=webhooks[1]),
            EventRule(name='EventRule 3', type_create=True, action_object=webhooks[2]),
        )
        for event in event_rules:
            event.save()
            event.object_types.add(site_type)

        webhook_ct = ContentType.objects.get_for_model(Webhook)
        cls.form_data = {
            'name': 'Event X',
            'object_types': [site_type.pk],
            'type_create': False,
            'type_update': True,
            'type_delete': True,
            'conditions': None,
            'action_type': 'webhook',
            'action_object_type': webhook_ct.pk,
            'action_object_id': webhooks[0].pk,
            'action_choice': webhooks[0],
            'description': 'New description',
        }

        cls.csv_data = (
            "name,object_types,type_create,action_type,action_object",
            "Webhook 4,dcim.site,True,webhook,Webhook 1",
        )

        cls.csv_update_data = (
            "id,name",
            f"{event_rules[0].pk},Event 7",
            f"{event_rules[1].pk},Event 8",
            f"{event_rules[2].pk},Event 9",
        )

        cls.bulk_edit_data = {
            'type_update': True,
        }


class TagTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Tag

    @classmethod
    def setUpTestData(cls):

        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)

        cls.form_data = {
            'name': 'Tag X',
            'slug': 'tag-x',
            'color': 'c0c0c0',
            'comments': 'Some comments',
        }

        cls.csv_data = (
            "name,slug,color,description",
            "Tag 4,tag-4,ff0000,Fourth tag",
            "Tag 5,tag-5,00ff00,Fifth tag",
            "Tag 6,tag-6,0000ff,Sixth tag",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{tags[0].pk},Tag 7,Fourth tag7",
            f"{tags[1].pk},Tag 8,Fifth tag8",
            f"{tags[2].pk},Tag 9,Sixth tag9",
        )

        cls.bulk_edit_data = {
            'color': '00ff00',
        }


# TODO: Change base class to PrimaryObjectViewTestCase
# Blocked by absence of standard create/edit, bulk create views
class ConfigContextTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = ConfigContext

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')

        # Create three ConfigContexts
        for i in range(1, 4):
            configcontext = ConfigContext(
                name='Config Context {}'.format(i),
                data={'foo': i}
            )
            configcontext.save()
            configcontext.device_types.add(devicetype)

        cls.form_data = {
            'name': 'Config Context X',
            'weight': 200,
            'description': 'A new config context',
            'is_active': True,
            'regions': [],
            'sites': [],
            'roles': [],
            'platforms': [],
            'tenant_groups': [],
            'tenants': [],
            'device_types': [devicetype.id],
            'tags': [],
            'data': '{"foo": 123}',
        }

        cls.bulk_edit_data = {
            'weight': 300,
            'is_active': False,
            'description': 'New description',
        }


class ConfigTemplateTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = ConfigTemplate

    @classmethod
    def setUpTestData(cls):
        TEMPLATE_CODE = """Foo: {{ foo }}"""

        config_templates = (
            ConfigTemplate(name='Config Template 1', template_code=TEMPLATE_CODE),
            ConfigTemplate(name='Config Template 2', template_code=TEMPLATE_CODE),
            ConfigTemplate(name='Config Template 3', template_code=TEMPLATE_CODE),
        )
        ConfigTemplate.objects.bulk_create(config_templates)

        cls.form_data = {
            'name': 'Config Template X',
            'description': 'Config template',
            'template_code': TEMPLATE_CODE,
        }

        cls.csv_update_data = (
            "id,name",
            f"{config_templates[0].pk},Config Template 7",
            f"{config_templates[1].pk},Config Template 8",
            f"{config_templates[2].pk},Config Template 9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


# TODO: Convert to StandardTestCases.Views
class ObjectChangeTestCase(TestCase):
    user_permissions = (
        'extras.view_objectchange',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        # Create three ObjectChanges
        user = User.objects.create_user(username='testuser2')
        for i in range(1, 4):
            oc = site.to_objectchange(action=ObjectChangeActionChoices.ACTION_UPDATE)
            oc.user = user
            oc.request_id = uuid.uuid4()
            oc.save()

    def test_objectchange_list(self):

        url = reverse('extras:objectchange_list')
        params = {
            "user": User.objects.first().pk,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_objectchange(self):

        objectchange = ObjectChange.objects.first()
        response = self.client.get(objectchange.get_absolute_url())
        self.assertHttpStatus(response, 200)


class JournalEntryTestCase(
    # ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = JournalEntry

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)

        site = Site.objects.create(name='Site 1', slug='site-1')
        user = User.objects.create(username='User 1')

        JournalEntry.objects.bulk_create((
            JournalEntry(assigned_object=site, created_by=user, comments='First entry'),
            JournalEntry(assigned_object=site, created_by=user, comments='Second entry'),
            JournalEntry(assigned_object=site, created_by=user, comments='Third entry'),
        ))

        cls.form_data = {
            'assigned_object_type': site_ct.pk,
            'assigned_object_id': site.pk,
            'kind': 'info',
            'comments': 'A new entry',
        }

        cls.bulk_edit_data = {
            'kind': 'success',
            'comments': 'Overwritten',
        }


class CustomLinkTest(TestCase):
    user_permissions = ['dcim.view_site']

    def test_view_object_with_custom_link(self):
        customlink = CustomLink(
            name='Test',
            link_text='FOO {{ object.name }} BAR',
            link_url='http://example.com/?site={{ object.slug }}',
            new_window=False
        )
        customlink.save()
        customlink.object_types.set([ObjectType.objects.get_for_model(Site)])

        site = Site(name='Test Site', slug='test-site')
        site.save()

        response = self.client.get(site.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'FOO {site.name} BAR', str(response.content))
