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
            'filter_logic': CustomFieldFilterLogicChoices.FILTER_EXACT,
            'default': None,
            'weight': 200,
            'required': True,
        }

        cls.csv_data = (
            "name,label,type,content_types,weight,filter_logic",
            "field4,Field 4,text,dcim.site,100,exact",
            "field5,Field 5,text,dcim.site,100,exact",
            "field6,Field 6,text,dcim.site,100,exact",
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
        CustomLink.objects.bulk_create((
            CustomLink(name='Custom Link 1', content_type=site_ct, link_text='Link 1', link_url='http://example.com/?1'),
            CustomLink(name='Custom Link 2', content_type=site_ct, link_text='Link 2', link_url='http://example.com/?2'),
            CustomLink(name='Custom Link 3', content_type=site_ct, link_text='Link 3', link_url='http://example.com/?3'),
        ))

        cls.form_data = {
            'name': 'Custom Link X',
            'content_type': site_ct.pk,
            'weight': 100,
            'button_class': CustomLinkButtonClassChoices.CLASS_DEFAULT,
            'link_text': 'Link X',
            'link_url': 'http://example.com/?x'
        }

        cls.csv_data = (
            "name,content_type,weight,button_class,link_text,link_url",
            "Custom Link 4,dcim.site,100,primary,Link 4,http://exmaple.com/?4",
            "Custom Link 5,dcim.site,100,primary,Link 5,http://exmaple.com/?5",
            "Custom Link 6,dcim.site,100,primary,Link 6,http://exmaple.com/?6",
        )

        cls.bulk_edit_data = {
            'button_class': CustomLinkButtonClassChoices.CLASS_INFO,
            'weight': 200,
        }


class ExportTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ExportTemplate

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)
        TEMPLATE_CODE = """{% for object in queryset %}{{ object }}{% endfor %}"""
        ExportTemplate.objects.bulk_create((
            ExportTemplate(name='Export Template 1', content_type=site_ct, template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 2', content_type=site_ct, template_code=TEMPLATE_CODE),
            ExportTemplate(name='Export Template 3', content_type=site_ct, template_code=TEMPLATE_CODE),
        ))

        cls.form_data = {
            'name': 'Export Template X',
            'content_type': site_ct.pk,
            'template_code': TEMPLATE_CODE,
        }

        cls.csv_data = (
            "name,content_type,template_code",
            f"Export Template 4,dcim.site,{TEMPLATE_CODE}",
            f"Export Template 5,dcim.site,{TEMPLATE_CODE}",
            f"Export Template 6,dcim.site,{TEMPLATE_CODE}",
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
        }

        cls.csv_data = (
            "name,content_types,type_create,payload_url,http_method,http_content_type",
            "Webhook 4,dcim.site,True,http://example.com/?4,GET,application/json",
            "Webhook 5,dcim.site,True,http://example.com/?5,GET,application/json",
            "Webhook 6,dcim.site,True,http://example.com/?6,GET,application/json",
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

        Tag.objects.bulk_create((
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        ))

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
            content_type=ContentType.objects.get_for_model(Site),
            name='Test',
            link_text='FOO {{ obj.name }} BAR',
            link_url='http://example.com/?site={{ obj.slug }}',
            new_window=False
        )
        customlink.save()

        site = Site(name='Test Site', slug='test-site')
        site.save()

        response = self.client.get(site.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'FOO {site.name} BAR', str(response.content))
