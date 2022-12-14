import urllib.parse
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from dcim.models import Site
from extras.choices import *
from extras.models import *
from utilities.testing import ViewTestCases, TestCase


class CustomFieldTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CustomField

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)
        custom_fields = (
            CustomField(name='field1', label='Field 1', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='field2', label='Field 2', type=CustomFieldTypeChoices.TYPE_TEXT),
            CustomField(name='field3', label='Field 3', type=CustomFieldTypeChoices.TYPE_TEXT),
        )
        for customfield in custom_fields:
            customfield.save()
            customfield.content_types.add(site_ct)

        cls.form_data = {
            'name': 'field_x',
            'label': 'Field X',
            'type': 'text',
            'content_types': [site_ct.pk],
            'search_weight': 2000,
            'filter_logic': CustomFieldFilterLogicChoices.FILTER_EXACT,
            'default': None,
            'weight': 200,
            'required': True,
            'ui_visibility': CustomFieldVisibilityChoices.VISIBILITY_READ_WRITE,
        }

        cls.csv_data = (
            'name,label,type,content_types,object_type,weight,search_weight,filter_logic,choices,validation_minimum,validation_maximum,validation_regex,ui_visibility',
            'field4,Field 4,text,dcim.site,,100,1000,exact,,,,[a-z]{3},read-write',
            'field5,Field 5,integer,dcim.site,,100,2000,exact,,1,100,,read-write',
            'field6,Field 6,select,dcim.site,,100,3000,exact,"A,B,C",,,,read-write',
            'field7,Field 7,object,dcim.site,dcim.region,100,4000,exact,,,,,read-write',
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


class CustomLinkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CustomLink

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)
        custom_links = (
            CustomLink(name='Custom Link 1', enabled=True, link_text='Link 1', link_url='http://example.com/?1'),
            CustomLink(name='Custom Link 2', enabled=True, link_text='Link 2', link_url='http://example.com/?2'),
            CustomLink(name='Custom Link 3', enabled=False, link_text='Link 3', link_url='http://example.com/?3'),
        )
        CustomLink.objects.bulk_create(custom_links)
        for i, custom_link in enumerate(custom_links):
            custom_link.content_types.set([site_ct])

        cls.form_data = {
            'name': 'Custom Link X',
            'content_types': [site_ct.pk],
            'enabled': False,
            'weight': 100,
            'button_class': CustomLinkButtonClassChoices.DEFAULT,
            'link_text': 'Link X',
            'link_url': 'http://example.com/?x'
        }

        cls.csv_data = (
            "name,content_types,enabled,weight,button_class,link_text,link_url",
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


class ExportTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ExportTemplate

    @classmethod
    def setUpTestData(cls):
        site_ct = ContentType.objects.get_for_model(Site)
        TEMPLATE_CODE = """{% for object in queryset %}{{ object }}{% endfor %}"""

        export_templates = (
            ExportTemplate(name='Export Template 1', template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 2', template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 3', template_code=TEMPLATE_CODE),
        )
        ExportTemplate.objects.bulk_create(export_templates)
        for et in export_templates:
            et.content_types.set([site_ct])

        cls.form_data = {
            'name': 'Export Template X',
            'content_types': [site_ct.pk],
            'template_code': TEMPLATE_CODE,
        }

        cls.csv_data = (
            "name,content_types,template_code",
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

        site_ct = ContentType.objects.get_for_model(Site)
        webhooks = (
            Webhook(name='Webhook 1', payload_url='http://example.com/?1', type_create=True, http_method='POST'),
            Webhook(name='Webhook 2', payload_url='http://example.com/?2', type_create=True, http_method='POST'),
            Webhook(name='Webhook 3', payload_url='http://example.com/?3', type_create=True, http_method='POST'),
        )
        for webhook in webhooks:
            webhook.save()
            webhook.content_types.add(site_ct)

        cls.form_data = {
            'name': 'Webhook X',
            'content_types': [site_ct.pk],
            'type_create': False,
            'type_update': True,
            'type_delete': True,
            'payload_url': 'http://example.com/?x',
            'http_method': 'GET',
            'http_content_type': 'application/foo',
            'conditions': None,
        }

        cls.csv_data = (
            "name,content_types,type_create,payload_url,http_method,http_content_type",
            "Webhook 4,dcim.site,True,http://example.com/?4,GET,application/json",
            "Webhook 5,dcim.site,True,http://example.com/?5,GET,application/json",
            "Webhook 6,dcim.site,True,http://example.com/?6,GET,application/json",
        )

        cls.csv_update_data = (
            "id,name",
            f"{webhooks[0].pk},Webhook 7",
            f"{webhooks[1].pk},Webhook 8",
            f"{webhooks[2].pk},Webhook 9",
        )

        cls.bulk_edit_data = {
            'enabled': False,
            'type_create': False,
            'type_update': True,
            'type_delete': True,
            'http_method': 'GET',
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

        site = Site.objects.create(name='Site 1', slug='site-1')

        # Create three ConfigContexts
        for i in range(1, 4):
            configcontext = ConfigContext(
                name='Config Context {}'.format(i),
                data={'foo': i}
            )
            configcontext.save()
            configcontext.sites.add(site)

        cls.form_data = {
            'name': 'Config Context X',
            'weight': 200,
            'description': 'A new config context',
            'is_active': True,
            'regions': [],
            'sites': [site.pk],
            'roles': [],
            'platforms': [],
            'tenant_groups': [],
            'tenants': [],
            'tags': [],
            'data': '{"foo": 123}',
        }

        cls.bulk_edit_data = {
            'weight': 300,
            'is_active': False,
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
            link_text='FOO {{ obj.name }} BAR',
            link_url='http://example.com/?site={{ obj.slug }}',
            new_window=False
        )
        customlink.save()
        customlink.content_types.set([ContentType.objects.get_for_model(Site)])

        site = Site(name='Test Site', slug='test-site')
        site.save()

        response = self.client.get(site.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'FOO {site.name} BAR', str(response.content))
