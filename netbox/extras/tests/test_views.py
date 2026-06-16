import uuid
from unittest.mock import PropertyMock, patch

from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.test import tag
from django.urls import reverse

from core.choices import JobStatusChoices, ManagedFileRootPathChoices
from core.events import *
from core.models import Job, ObjectType
from dcim.models import DeviceType, Manufacturer, Site
from extras.choices import *
from extras.models import *
from extras.scripts import BooleanVar, IntegerVar
from extras.scripts import Script as PythonClass
from users.models import Group, ObjectPermission, User
from utilities.testing import TestCase, ViewTestCases


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
            'name,label,type,object_types,related_object_type,weight,search_weight,filter_logic,choice_set,validation_minimum,validation_maximum,validation_regex,ui_visible,ui_editable',
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


class CustomLinkRenderingTestCase(TestCase):
    user_permissions = ['dcim.view_site', 'extras.view_customlink']

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


class SavedFilterTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = SavedFilter

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)

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
            savedfilter.object_types.set([site_type])

        cls.form_data = {
            'name': 'Saved Filter X',
            'slug': 'saved-filter-x',
            'object_types': [site_type.pk],
            'description': 'Foo',
            'weight': 1000,
            'enabled': True,
            'shared': True,
            'parameters': '{"foo": 123}',
        }

        cls.csv_data = (
            'name,slug,object_types,weight,enabled,shared,parameters',
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


class TableConfigTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = TableConfig
    # Selected columns are POSTed as a list but compared as a CSV string
    validation_excluded_fields = ('columns',)

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)
        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        table_configs = (
            TableConfig(
                name='Table Config 1',
                object_type=site_type,
                table='SiteTable',
                user=users[0],
                columns=['name', 'status'],
            ),
            TableConfig(
                name='Table Config 2',
                object_type=site_type,
                table='SiteTable',
                user=users[1],
                columns=['name', 'region'],
            ),
            TableConfig(
                name='Table Config 3',
                object_type=site_type,
                table='SiteTable',
                user=users[2],
                columns=['name', 'tenant'],
            ),
        )
        TableConfig.objects.bulk_create(table_configs)

        cls.form_data = {
            'name': 'Table Config X',
            'object_type': site_type.pk,
            'table': 'SiteTable',
            'description': 'A table config',
            'weight': 100,
            'enabled': True,
            'shared': True,
            'columns': ['name', 'status'],
            'ordering': 'name',
        }
        cls.bulk_edit_data = {
            'weight': 999,
        }

    def _get_url(self, action, instance=None):
        url = super()._get_url(action, instance)
        # The add view requires the table context from the source table view
        if action == 'add':
            site_type = ObjectType.objects.get_for_model(Site)
            url = f'{url}?object_type={site_type.pk}&table=SiteTable'
        return url

    def test_add_view_without_table_context(self):
        """A GET without the table context params must redirect to the home page."""
        self.add_permissions('extras.add_tableconfig')
        response = self.client.get(reverse('extras:tableconfig_add'))
        self.assertRedirects(response, reverse('home'))

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Table configurations must be created from an object list view.')

    def test_add_view_post_without_table_context(self):
        """A POST without the table context must return form errors rather than a server error."""
        self.add_permissions('extras.add_tableconfig')
        response = self.client.post(reverse('extras:tableconfig_add'), data={})
        self.assertHttpStatus(response, 200)


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

    def test_export_objects_anonymous(self):
        return

    def test_list_objects_with_constrained_permission(self):
        return


class ImageAttachmentTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    # Add/Edit/BulkEdit are omitted: ImageField.save() re-reads the file to
    # populate image_height / image_width, which fails when fixtures use
    # placeholder URLs instead of real images on disk.
    model = ImageAttachment

    @classmethod
    def setUpTestData(cls):
        ct = ContentType.objects.get_for_model(Site)
        site = Site.objects.create(name='Site 1', slug='site-1')

        ImageAttachment.objects.bulk_create(
            [
                ImageAttachment(
                    object_type=ct,
                    object_id=site.pk,
                    name='Image Attachment 1',
                    image='http://example.com/image1.png',
                    image_height=100,
                    image_width=100,
                ),
                ImageAttachment(
                    object_type=ct,
                    object_id=site.pk,
                    name='Image Attachment 2',
                    image='http://example.com/image2.png',
                    image_height=100,
                    image_width=100,
                ),
                ImageAttachment(
                    object_type=ct,
                    object_id=site.pk,
                    name='Image Attachment 3',
                    image='http://example.com/image3.png',
                    image_height=100,
                    image_width=100,
                ),
            ]
        )


class ExportTemplateTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ExportTemplate

    @classmethod
    def setUpTestData(cls):
        site_type = ObjectType.objects.get_for_model(Site)
        TEMPLATE_CODE = """{% for object in queryset %}{{ object }}{% endfor %}"""
        ENVIRONMENT_PARAMS = """{"trim_blocks": true}"""

        export_templates = (
            ExportTemplate(name='Export Template 1', template_code=TEMPLATE_CODE),
            ExportTemplate(
                name='Export Template 2', template_code=TEMPLATE_CODE, environment_params={"trim_blocks": True}
            ),
            ExportTemplate(name='Export Template 3', template_code=TEMPLATE_CODE, file_name='export_template_3')
        )
        ExportTemplate.objects.bulk_create(export_templates)
        for et in export_templates:
            et.object_types.set([site_type])

        cls.form_data = {
            'name': 'Export Template X',
            'object_types': [site_type.pk],
            'template_code': TEMPLATE_CODE,
            'environment_params': ENVIRONMENT_PARAMS,
            'file_name': 'template_x',
        }

        cls.csv_data = (
            "name,object_types,template_code,file_name",
            f"Export Template 4,dcim.site,{TEMPLATE_CODE},",
            f"Export Template 5,dcim.site,{TEMPLATE_CODE},template_5",
            f"Export Template 6,dcim.site,{TEMPLATE_CODE},",
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


class ExportTemplateExportFlowTestCase(TestCase):
    """
    End-to-end test for ExportTemplate invocation via a list view's ?export=<name> query param.
    """

    @classmethod
    def setUpTestData(cls):
        Site.objects.bulk_create([
            Site(name='Site A', slug='site-a'),
            Site(name='Site B', slug='site-b'),
        ])

        site_type = ObjectType.objects.get_for_model(Site)

        ok_template = ExportTemplate.objects.create(
            name='Sites Export',
            template_code='{% for obj in queryset %}{{ obj.name }}\n{% endfor %}',
            mime_type='text/plain',
            file_extension='txt',
        )
        ok_template.object_types.set([site_type])

        broken_template = ExportTemplate.objects.create(
            name='Broken Export',
            template_code='{% for obj in queryset %}{{ obj.name ',  # unterminated expression
        )
        broken_template.object_types.set([site_type])

    def test_export_template_invocation(self):
        self.add_permissions('dcim.view_site', 'extras.view_exporttemplate')
        url = reverse('dcim:site_list')

        response = self.client.get(f'{url}?export=Sites Export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="netbox_sites.txt"')
        # The rendered queryset reflects whatever ordering the list view applies. Assert on set
        # membership rather than line order so the test isn't coupled to Site's natural ordering.
        rendered_names = set(filter(None, response.content.decode().split('\n')))
        self.assertEqual(rendered_names, {'Site A', 'Site B'})

    def test_export_template_render_error_redirects(self):
        self.add_permissions('dcim.view_site', 'extras.view_exporttemplate')
        url = reverse('dcim:site_list')

        # A broken template surfaces an exception during render; the view catches it and redirects
        # back to the (filtered) list view rather than returning a 500.
        response = self.client.get(f'{url}?export=Broken Export')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(url))
        self.assertNotIn('export=', response['Location'])


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
            EventRule(name='EventRule 1', event_types=[OBJECT_CREATED], action_object=webhooks[0]),
            EventRule(name='EventRule 2', event_types=[OBJECT_CREATED], action_object=webhooks[1]),
            EventRule(name='EventRule 3', event_types=[OBJECT_CREATED], action_object=webhooks[2]),
        )
        for event in event_rules:
            event.save()
            event.object_types.add(site_type)

        webhook_ct = ContentType.objects.get_for_model(Webhook)
        cls.form_data = {
            'name': 'Event X',
            'object_types': [site_type.pk],
            'event_types': [OBJECT_UPDATED, OBJECT_DELETED],
            'conditions': None,
            'action_type': 'webhook',
            'action_object_type': webhook_ct.pk,
            'action_object_id': webhooks[0].pk,
            'action_choice': webhooks[0],
            'description': 'New description',
        }

        cls.csv_data = (
            'name,object_types,event_types,action_type,action_object',
            f'Webhook 4,dcim.site,"{OBJECT_CREATED},{OBJECT_UPDATED}",webhook,Webhook 1',
        )

        cls.csv_update_data = (
            "id,name",
            f"{event_rules[0].pk},Event 7",
            f"{event_rules[1].pk},Event 8",
            f"{event_rules[2].pk},Event 9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class TagTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Tag

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get_for_model(Site)

        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2', weight=1),
            Tag(name='Tag 3', slug='tag-3', weight=32767),
        )
        Tag.objects.bulk_create(tags)

        cls.form_data = {
            'name': 'Tag X',
            'slug': 'tag-x',
            'color': 'c0c0c0',
            'comments': 'Some comments',
            'object_types': [site_ct.pk],
            'weight': 11,
        }

        cls.csv_data = (
            "name,slug,color,description,object_types,weight",
            "Tag 4,tag-4,ff0000,Fourth tag,dcim.interface,0",
            "Tag 5,tag-5,00ff00,Fifth tag,'dcim.device,dcim.site',1111",
            "Tag 6,tag-6,0000ff,Sixth tag,dcim.site,0",
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


class ConfigContextProfileTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ConfigContextProfile

    @classmethod
    def setUpTestData(cls):
        profiles = (
            ConfigContextProfile(
                name='Config Context Profile 1',
                schema={
                    "properties": {
                        "foo": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "foo"
                    ]
                }
            ),
            ConfigContextProfile(
                name='Config Context Profile 2',
                schema={
                    "properties": {
                        "bar": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "bar"
                    ]
                }
            ),
            ConfigContextProfile(
                name='Config Context Profile 3',
                schema={
                    "properties": {
                        "baz": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "baz"
                    ]
                }
            ),
        )
        ConfigContextProfile.objects.bulk_create(profiles)

        cls.form_data = {
            'name': 'Config Context Profile X',
            'description': 'A new config context profile',
        }

        cls.bulk_edit_data = {
            'description': 'New description',
        }

        cls.csv_data = (
            'name,description',
            'Config context profile 1,Foo',
            'Config context profile 2,Bar',
            'Config context profile 3,Baz',
        )

        cls.csv_update_data = (
            "id,description",
            f"{profiles[0].pk},New description",
            f"{profiles[1].pk},New description",
            f"{profiles[2].pk},New description",
        )


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
        ENVIRONMENT_PARAMS = """{"trim_blocks": true}"""

        config_templates = (
            ConfigTemplate(
                name='Config Template 1',
                template_code=TEMPLATE_CODE)
            ,
            ConfigTemplate(
                name='Config Template 2',
                template_code=TEMPLATE_CODE,
                environment_params={"trim_blocks": True},
            ),
            ConfigTemplate(
                name='Config Template 3',
                template_code=TEMPLATE_CODE,
                file_name='config_template_3',
            ),
        )
        ConfigTemplate.objects.bulk_create(config_templates)

        cls.form_data = {
            'name': 'Config Template X',
            'description': 'Config template',
            'template_code': TEMPLATE_CODE,
            'environment_params': ENVIRONMENT_PARAMS,
            'file_name': 'config_x',
        }

        cls.csv_update_data = (
            "id,name",
            f"{config_templates[0].pk},Config Template 7",
            f"{config_templates[1].pk},Config Template 8",
            f"{config_templates[2].pk},Config Template 9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
            'mime_type': 'text/html',
            'file_name': 'output',
            'file_extension': 'html',
            'as_attachment': True,
        }


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


class SubscriptionTestCase(
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = Subscription

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

        subscriptions = (
            Subscription(object=sites[0], user=user),
            Subscription(object=sites[1], user=user),
            Subscription(object=sites[2], user=user),
        )
        Subscription.objects.bulk_create(subscriptions)

    def _get_url(self, action, instance=None):
        if action == 'list':
            return reverse('account:subscriptions')
        return super()._get_url(action, instance)

    def test_list_objects_anonymous(self):
        self.client.logout()
        url = reverse('account:subscriptions')
        login_url = reverse('login')
        self.assertRedirects(self.client.get(url), f'{login_url}?next={url}')

    def test_export_objects_anonymous(self):
        return

    def test_list_objects_with_permission(self):
        return

    def test_list_objects_with_constrained_permission(self):
        return


class NotificationGroupTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = NotificationGroup

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

        cls.form_data = {
            'name': 'Notification Group X',
            'description': 'Blah',
            'users': [users[0].pk, users[1].pk],
            'groups': [groups[0].pk, groups[1].pk],
        }

        cls.csv_data = (
            'name,description,users,groups',
            'Notification Group 4,Foo,"User 1,User 2","Group 1,Group 2"',
            'Notification Group 5,Bar,"User 1,User 2","Group 1,Group 2"',
            'Notification Group 6,Baz,"User 1,User 2","Group 1,Group 2"',
        )

        cls.csv_update_data = (
            "id,name",
            f"{notification_groups[0].pk},Notification Group 7",
            f"{notification_groups[1].pk},Notification Group 8",
            f"{notification_groups[2].pk},Notification Group 9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class NotificationTestCase(
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = Notification

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

        notifications = (
            Notification(object=sites[0], user=user),
            Notification(object=sites[1], user=user),
            Notification(object=sites[2], user=user),
        )
        Notification.objects.bulk_create(notifications)

    def _get_url(self, action, instance=None):
        if action == 'list':
            return reverse('account:notifications')
        return super()._get_url(action, instance)

    def test_list_objects_anonymous(self):
        self.client.logout()
        url = reverse('account:notifications')
        login_url = reverse('login')
        self.assertRedirects(self.client.get(url), f'{login_url}?next={url}')

    def test_export_objects_anonymous(self):
        return

    def test_list_objects_with_permission(self):
        return

    def test_list_objects_with_constrained_permission(self):
        return


class ScriptListViewTestCase(TestCase):
    user_permissions = ['extras.view_script']

    def test_script_list_embedded_parameter(self):
        """Test that ScriptListView accepts embedded parameter without error"""
        url = reverse('extras:script_list')

        # Test normal request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extras/script_list.html')

        # Test embedded request
        response = self.client.get(url, {'embedded': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'extras/inc/script_list_content.html')


class ScriptValidationErrorTestCase(TestCase):
    user_permissions = ['extras.view_script', 'extras.run_script']

    class TestScriptMixin:
        bar = IntegerVar(min_value=0, max_value=30)

    class TestScriptClass(TestScriptMixin, PythonClass):
        class Meta:
            name = 'Test script'
            commit_default = False
            fieldsets = (("Logging", ("debug_mode",)),)

        debug_mode = BooleanVar(default=False)

        def run(self, data, commit):
            return "Complete"

    @classmethod
    def setUpTestData(cls):
        # Avoid trying to import a non-existent on-disk module during setup.
        # This test creates the Script row explicitly and monkey-patches
        # Script.python_class below.
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='test_script.py',
            )
        cls.script = Script.objects.create(module=module, name='Test script', is_executable=True)

    def setUp(self):
        super().setUp()
        Script.python_class = property(lambda self: ScriptValidationErrorTestCase.TestScriptClass)

    @tag('regression')
    def test_script_validation_error_displays_message(self):
        url = reverse('extras:script', kwargs={'pk': self.script.pk})

        with patch('extras.views.any_workers_for_queue', return_value=True):
            response = self.client.post(url, {'debug_mode': 'true', '_commit': 'true'})

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "bar: This field is required.")

    @tag('regression')
    def test_script_validation_error_no_toast_for_fieldset_fields(self):
        class FieldsetScript(PythonClass):
            class Meta:
                name = 'Fieldset test'
                commit_default = False
                fieldsets = (("Fields", ("required_field",)),)

            required_field = IntegerVar(min_value=10)

            def run(self, data, commit):
                return "Complete"

        url = reverse('extras:script', kwargs={'pk': self.script.pk})

        with patch.object(Script, 'python_class', new_callable=PropertyMock) as mock_python_class:
            mock_python_class.return_value = FieldsetScript
            with patch('extras.views.any_workers_for_queue', return_value=True):
                response = self.client.post(url, {'required_field': '5', '_commit': 'true'})

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)


class ScriptDefaultValuesTestCase(TestCase):
    user_permissions = ['extras.view_script', 'extras.run_script']

    class TestScriptClass(PythonClass):
        class Meta:
            name = 'Test script'
            commit_default = False

        bool_default_true = BooleanVar(default=True)
        bool_default_false = BooleanVar(default=False)
        int_with_default = IntegerVar(default=0)
        int_without_default = IntegerVar(required=False)

        def run(self, data, commit):
            return "Complete"

    @classmethod
    def setUpTestData(cls):
        # Avoid trying to import a non-existent on-disk module during setup.
        # This test creates the Script row explicitly and monkey-patches
        # Script.python_class below.
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='test_script.py',
            )
        cls.script = Script.objects.create(module=module, name='Test script', is_executable=True)

    def setUp(self):
        super().setUp()
        Script.python_class = property(lambda self: ScriptDefaultValuesTestCase.TestScriptClass)

    def test_default_values_are_used(self):
        url = reverse('extras:script', kwargs={'pk': self.script.pk})

        with patch('extras.views.any_workers_for_queue', return_value=True):
            with patch('extras.jobs.ScriptJob.enqueue') as mock_enqueue:
                mock_enqueue.return_value.pk = 1
                self.client.post(url, {})
                call_kwargs = mock_enqueue.call_args.kwargs
                self.assertEqual(call_kwargs['data']['bool_default_true'], True)
                self.assertEqual(call_kwargs['data']['bool_default_false'], False)
                self.assertEqual(call_kwargs['data']['int_with_default'], 0)
                self.assertIsNone(call_kwargs['data']['int_without_default'])


class ScriptResultViewTestCase(TestCase):
    SECRET_OUTPUT = 'my secret script output'

    @classmethod
    def setUpTestData(cls):
        with patch.object(ScriptModule, 'sync_classes'):
            module = ScriptModule.objects.create(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='test_script.py',
            )
        cls.allowed_script = Script.objects.create(
            module=module, name='Allowed script', is_executable=True
        )
        cls.secret_script = Script.objects.create(
            module=module, name='Secret script', is_executable=True
        )

        script_type = ObjectType.objects.get_for_model(Script)
        cls.allowed_job = Job.objects.create(
            object_type=script_type,
            object_id=cls.allowed_script.pk,
            name='allowed-job',
            job_id=uuid.uuid4(),
            status=JobStatusChoices.STATUS_COMPLETED,
            data={'log': [], 'output': 'benign output'},
        )
        cls.secret_job = Job.objects.create(
            object_type=script_type,
            object_id=cls.secret_script.pk,
            name='secret-job',
            job_id=uuid.uuid4(),
            status=JobStatusChoices.STATUS_COMPLETED,
            data={'log': [], 'output': cls.SECRET_OUTPUT},
        )

    def test_get_without_view_job_permission_returns_404(self):
        """
        A user with extras.view_script but no core.view_job must not retrieve any job result
        via ScriptResultView, even for the script whose object-level permission they hold.
        """
        self.add_permissions('extras.view_script')

        url = reverse('extras:script_result', kwargs={'job_pk': self.allowed_job.pk})
        self.assertHttpStatus(self.client.get(url), 404)

        url = reverse('extras:script_result', kwargs={'job_pk': self.secret_job.pk})
        self.assertHttpStatus(self.client.get(url), 404)

    def test_get_export_output_without_view_job_permission_returns_404(self):
        """
        Regression for the PoC: the ?export=output path must not leak job.data['output']
        when the user lacks core.view_job.
        """
        self.add_permissions('extras.view_script')

        url = reverse('extras:script_result', kwargs={'job_pk': self.secret_job.pk})
        response = self.client.get(url, {'export': 'output'})

        self.assertHttpStatus(response, 404)
        self.assertNotIn(self.SECRET_OUTPUT.encode(), response.content)

    def test_get_with_constrained_view_job_permission(self):
        """
        With core.view_job constrained to the allowed job only, the user can fetch the allowed
        result but the secret result is hidden (404).
        """
        self.add_permissions('extras.view_script')
        obj_perm = ObjectPermission(
            name='View allowed job only',
            constraints={'pk': self.allowed_job.pk},
            actions=['view'],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Job))

        url = reverse('extras:script_result', kwargs={'job_pk': self.allowed_job.pk})
        self.assertHttpStatus(self.client.get(url), 200)

        url = reverse('extras:script_result', kwargs={'job_pk': self.secret_job.pk})
        response = self.client.get(url, {'export': 'output'})
        self.assertHttpStatus(response, 404)
        self.assertNotIn(self.SECRET_OUTPUT.encode(), response.content)
