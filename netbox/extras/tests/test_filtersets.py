import uuid
from datetime import datetime, timezone

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.models import Provider
from core.choices import ManagedFileRootPathChoices, ObjectChangeActionChoices
from core.events import *
from core.models import ObjectChange, ObjectType
from dcim.filtersets import SiteFilterSet
from dcim.models import DeviceRole, DeviceType, Manufacturer, Platform, Rack, Region, Site, SiteGroup
from dcim.models import Location
from extras.choices import *
from extras.filtersets import *
from extras.models import *
from tenancy.models import Tenant, TenantGroup
from users.models import Group, User
from utilities.testing import BaseFilterSetTests, ChangeLoggedFilterSetTests, create_tags
from virtualization.models import Cluster, ClusterGroup, ClusterType


class CustomFieldTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CustomField.objects.all()
    filterset = CustomFieldFilterSet
    ignore_fields = ('default', 'related_object_filter')

    @classmethod
    def setUpTestData(cls):
        choice_sets = (
            CustomFieldChoiceSet(name='Choice Set 1', extra_choices=['A', 'B', 'C']),
            CustomFieldChoiceSet(name='Choice Set 2', extra_choices=['D', 'E', 'F']),
        )
        CustomFieldChoiceSet.objects.bulk_create(choice_sets)

        custom_fields = (
            CustomField(
                name='Custom Field 1',
                type=CustomFieldTypeChoices.TYPE_TEXT,
                required=True,
                weight=100,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_LOOSE,
                ui_visible=CustomFieldUIVisibleChoices.ALWAYS,
                ui_editable=CustomFieldUIEditableChoices.YES,
                description='foobar1'
            ),
            CustomField(
                name='Custom Field 2',
                type=CustomFieldTypeChoices.TYPE_INTEGER,
                required=False,
                weight=200,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_EXACT,
                ui_visible=CustomFieldUIVisibleChoices.IF_SET,
                ui_editable=CustomFieldUIEditableChoices.NO,
                description='foobar2'
            ),
            CustomField(
                name='Custom Field 3',
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                required=False,
                weight=300,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED,
                ui_visible=CustomFieldUIVisibleChoices.HIDDEN,
                ui_editable=CustomFieldUIEditableChoices.HIDDEN,
                description='foobar3'
            ),
            CustomField(
                name='Custom Field 4',
                type=CustomFieldTypeChoices.TYPE_SELECT,
                required=False,
                weight=400,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED,
                ui_visible=CustomFieldUIVisibleChoices.HIDDEN,
                ui_editable=CustomFieldUIEditableChoices.HIDDEN,
                choice_set=choice_sets[0]
            ),
            CustomField(
                name='Custom Field 5',
                type=CustomFieldTypeChoices.TYPE_MULTISELECT,
                required=False,
                weight=500,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED,
                ui_visible=CustomFieldUIVisibleChoices.HIDDEN,
                ui_editable=CustomFieldUIEditableChoices.HIDDEN,
                choice_set=choice_sets[1]
            ),
            CustomField(
                name='Custom Field 6',
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                related_object_type=ObjectType.objects.get_by_natural_key('dcim', 'site'),
                required=False,
                weight=600,
                filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED,
                ui_visible=CustomFieldUIVisibleChoices.HIDDEN,
                ui_editable=CustomFieldUIEditableChoices.HIDDEN
            ),
        )
        CustomField.objects.bulk_create(custom_fields)
        custom_fields[0].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'site'))
        custom_fields[1].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'rack'))
        custom_fields[2].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'device'))
        custom_fields[3].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'device'))
        custom_fields[4].object_types.add(ObjectType.objects.get_by_natural_key('dcim', 'device'))

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Custom Field 1', 'Custom Field 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'object_type_id': [ObjectType.objects.get_by_natural_key('dcim', 'site').pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_related_object_type(self):
        params = {'related_object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'related_object_type_id': [ObjectType.objects.get_by_natural_key('dcim', 'site').pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_required(self):
        params = {'required': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_weight(self):
        params = {'weight': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_filter_logic(self):
        params = {'filter_logic': CustomFieldFilterLogicChoices.FILTER_LOOSE}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_ui_visible(self):
        params = {'ui_visible': CustomFieldUIVisibleChoices.ALWAYS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_ui_editable(self):
        params = {'ui_editable': CustomFieldUIEditableChoices.YES}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_choice_set(self):
        params = {'choice_set': ['Choice Set 1', 'Choice Set 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'choice_set_id': CustomFieldChoiceSet.objects.values_list('pk', flat=True)}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CustomFieldChoiceSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CustomFieldChoiceSet.objects.all()
    filterset = CustomFieldChoiceSetFilterSet
    ignore_fields = ('extra_choices',)

    @classmethod
    def setUpTestData(cls):
        choice_sets = (
            CustomFieldChoiceSet(name='Choice Set 1', extra_choices=['A', 'B', 'C'], description='foobar1'),
            CustomFieldChoiceSet(name='Choice Set 2', extra_choices=['D', 'E', 'F'], description='foobar2'),
            CustomFieldChoiceSet(name='Choice Set 3', extra_choices=['G', 'H', 'I'], description='foobar3'),
        )
        CustomFieldChoiceSet.objects.bulk_create(choice_sets)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Choice Set 1', 'Choice Set 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_choice(self):
        params = {'choice': ['A', 'D']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class WebhookTestCase(TestCase, BaseFilterSetTests):
    queryset = Webhook.objects.all()
    filterset = WebhookFilterSet
    ignore_fields = ('additional_headers', 'body_template')

    @classmethod
    def setUpTestData(cls):
        webhooks = (
            Webhook(
                name='Webhook 1',
                payload_url='http://example.com/?1',
                http_method='GET',
                ssl_verification=True,
                description='foobar1'
            ),
            Webhook(
                name='Webhook 2',
                payload_url='http://example.com/?2',
                http_method='POST',
                ssl_verification=True,
                description='foobar2'
            ),
            Webhook(
                name='Webhook 3',
                payload_url='http://example.com/?3',
                http_method='PATCH',
                ssl_verification=False,
                description='foobar3'
            ),
            Webhook(
                name='Webhook 4',
                payload_url='http://example.com/?4',
                http_method='PATCH',
                ssl_verification=False,
            ),
            Webhook(
                name='Webhook 5',
                payload_url='http://example.com/?5',
                http_method='PATCH',
                ssl_verification=False,
            ),
        )
        Webhook.objects.bulk_create(webhooks)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Webhook 1', 'Webhook 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_http_method(self):
        params = {'http_method': ['GET', 'POST']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ssl_verification(self):
        params = {'ssl_verification': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class EventRuleTestCase(TestCase, BaseFilterSetTests):
    queryset = EventRule.objects.all()
    filterset = EventRuleFilterSet
    ignore_fields = ('action_data', 'conditions', 'event_types')

    @classmethod
    def setUpTestData(cls):
        object_types = ObjectType.objects.filter(
            model__in=['region', 'site', 'rack', 'location', 'device']
        )

        webhooks = (
            Webhook(
                name='Webhook 1',
                payload_url='http://example.com/?1',
            ),
            Webhook(
                name='Webhook 2',
                payload_url='http://example.com/?2',
            ),
            Webhook(
                name='Webhook 3',
                payload_url='http://example.com/?3',
            ),
        )
        Webhook.objects.bulk_create(webhooks)

        scripts = (
            ScriptModule(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='/var/tmp/script1.py'
            ),
            ScriptModule(
                file_root=ManagedFileRootPathChoices.SCRIPTS,
                file_path='/var/tmp/script2.py'
            ),
        )
        ScriptModule.objects.bulk_create(scripts)

        event_rules = (
            EventRule(
                name='Event Rule 1',
                action_object=webhooks[0],
                enabled=True,
                event_types=[OBJECT_CREATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                description='foobar1'
            ),
            EventRule(
                name='Event Rule 2',
                action_object=webhooks[1],
                enabled=True,
                event_types=[OBJECT_UPDATED],
                action_type=EventRuleActionChoices.WEBHOOK,
                description='foobar2'
            ),
            EventRule(
                name='Event Rule 3',
                action_object=webhooks[2],
                enabled=False,
                event_types=[OBJECT_DELETED],
                action_type=EventRuleActionChoices.WEBHOOK,
                description='foobar3'
            ),
            EventRule(
                name='Event Rule 4',
                action_object=scripts[0],
                enabled=False,
                event_types=[JOB_STARTED],
                action_type=EventRuleActionChoices.SCRIPT,
            ),
            EventRule(
                name='Event Rule 5',
                action_object=scripts[1],
                enabled=False,
                event_types=[JOB_COMPLETED],
                action_type=EventRuleActionChoices.SCRIPT,
            ),
        )
        EventRule.objects.bulk_create(event_rules)
        event_rules[0].object_types.add(object_types[0])
        event_rules[1].object_types.add(object_types[1])
        event_rules[2].object_types.add(object_types[2])
        event_rules[3].object_types.add(object_types[3])
        event_rules[4].object_types.add(object_types[4])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Event Rule 1', 'Event Rule 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.region'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'object_type_id': [ObjectType.objects.get_for_model(Region).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_action_type(self):
        params = {'action_type': [EventRuleActionChoices.WEBHOOK]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'action_type': [EventRuleActionChoices.SCRIPT]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_event_type(self):
        params = {'event_type': [OBJECT_CREATED, OBJECT_UPDATED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CustomLinkTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = CustomLink.objects.all()
    filterset = CustomLinkFilterSet

    @classmethod
    def setUpTestData(cls):
        object_types = ObjectType.objects.filter(model__in=['site', 'rack', 'device'])

        custom_links = (
            CustomLink(
                name='Custom Link 1',
                enabled=True,
                weight=100,
                new_window=False,
                link_text='Link 1',
                link_url='http://example.com/?1'
            ),
            CustomLink(
                name='Custom Link 2',
                enabled=True,
                weight=200,
                new_window=False,
                link_text='Link 1',
                link_url='http://example.com/?2'
            ),
            CustomLink(
                name='Custom Link 3',
                enabled=False,
                weight=300,
                new_window=True,
                link_text='Link 1',
                link_url='http://example.com/?3'
            ),
        )
        CustomLink.objects.bulk_create(custom_links)
        for i, custom_link in enumerate(custom_links):
            custom_link.object_types.set([object_types[i]])

    def test_q(self):
        params = {'q': 'Custom Link 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Custom Link 1', 'Custom Link 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'object_type_id': [ObjectType.objects.get_for_model(Site).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_weight(self):
        params = {'weight': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_new_window(self):
        params = {'new_window': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'new_window': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class SavedFilterTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = SavedFilter.objects.all()
    filterset = SavedFilterFilterSet
    ignore_fields = ('parameters',)

    @classmethod
    def setUpTestData(cls):
        object_types = ObjectType.objects.filter(model__in=['site', 'rack', 'device'])

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
                enabled=True,
                shared=True,
                parameters={'status': ['active']},
                description='foobar1'
            ),
            SavedFilter(
                name='Saved Filter 2',
                slug='saved-filter-2',
                user=users[1],
                weight=200,
                enabled=True,
                shared=True,
                parameters={'status': ['planned']},
                description='foobar2'
            ),
            SavedFilter(
                name='Saved Filter 3',
                slug='saved-filter-3',
                user=users[2],
                weight=300,
                enabled=False,
                shared=False,
                parameters={'status': ['retired']},
                description='foobar3'
            ),
        )
        SavedFilter.objects.bulk_create(saved_filters)
        for i, savedfilter in enumerate(saved_filters):
            savedfilter.object_types.set([object_types[i]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Saved Filter 1', 'Saved Filter 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['saved-filter-1', 'saved-filter-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'object_type_id': [ObjectType.objects.get_for_model(Site).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_user(self):
        users = User.objects.filter(username__startswith='User')
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight(self):
        params = {'weight': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_shared(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_usable(self):
        # Filtering for an anonymous user
        params = {'usable': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'usable': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class BookmarkTestCase(TestCase, BaseFilterSetTests):
    queryset = Bookmark.objects.all()
    filterset = BookmarkFilterSet

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        bookmarks = (
            Bookmark(
                object=sites[0],
                user=users[0],
            ),
            Bookmark(
                object=sites[1],
                user=users[1],
            ),
            Bookmark(
                object=sites[2],
                user=users[2],
            ),
            Bookmark(
                object=tenants[0],
                user=users[0],
            ),
            Bookmark(
                object=tenants[1],
                user=users[1],
            ),
            Bookmark(
                object=tenants[2],
                user=users[2],
            ),
        )
        Bookmark.objects.bulk_create(bookmarks)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'object_type_id': [ContentType.objects.get_for_model(Site).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_user(self):
        users = User.objects.filter(username__startswith='User')
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class ExportTemplateTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ExportTemplate.objects.all()
    filterset = ExportTemplateFilterSet
    ignore_fields = ('template_code', 'data_path')

    @classmethod
    def setUpTestData(cls):
        object_types = ObjectType.objects.filter(model__in=['site', 'rack', 'device'])

        export_templates = (
            ExportTemplate(name='Export Template 1', template_code='TESTING', description='foobar1'),
            ExportTemplate(name='Export Template 2', template_code='TESTING', description='foobar2'),
            ExportTemplate(name='Export Template 3', template_code='TESTING'),
        )
        ExportTemplate.objects.bulk_create(export_templates)
        for i, et in enumerate(export_templates):
            et.object_types.set([object_types[i]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Export Template 1', 'Export Template 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'object_type_id': [ObjectType.objects.get_for_model(Site).pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ImageAttachmentTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ImageAttachment.objects.all()
    filterset = ImageAttachmentFilterSet
    ignore_fields = ('image',)

    @classmethod
    def setUpTestData(cls):

        site_ct = ContentType.objects.get(app_label='dcim', model='site')
        rack_ct = ContentType.objects.get(app_label='dcim', model='rack')

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        image_attachments = (
            ImageAttachment(
                object_type=site_ct,
                object_id=sites[0].pk,
                name='Image Attachment 1',
                image='http://example.com/image1.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                object_type=site_ct,
                object_id=sites[1].pk,
                name='Image Attachment 2',
                image='http://example.com/image2.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                object_type=rack_ct,
                object_id=racks[0].pk,
                name='Image Attachment 3',
                image='http://example.com/image3.png',
                image_height=100,
                image_width=100
            ),
            ImageAttachment(
                object_type=rack_ct,
                object_id=racks[1].pk,
                name='Image Attachment 4',
                image='http://example.com/image4.png',
                image_height=100,
                image_width=100
            )
        )
        ImageAttachment.objects.bulk_create(image_attachments)

    def test_q(self):
        params = {'q': 'Attachment 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Image Attachment 1', 'Image Attachment 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type_id_and_object_id(self):
        params = {
            'object_type_id': ContentType.objects.get(app_label='dcim', model='site').pk,
            'object_id': [Site.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class JournalEntryTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = JournalEntry.objects.all()
    filterset = JournalEntryFilterSet

    @classmethod
    def setUpTestData(cls):
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        users = (
            User(username='Alice'),
            User(username='Bob'),
            User(username='Charlie'),
        )
        User.objects.bulk_create(users)

        journal_entries = (
            JournalEntry(
                assigned_object=sites[0],
                created_by=users[0],
                kind=JournalEntryKindChoices.KIND_INFO,
                comments='foobar1'
            ),
            JournalEntry(
                assigned_object=sites[0],
                created_by=users[1],
                kind=JournalEntryKindChoices.KIND_SUCCESS,
                comments='foobar2'
            ),
            JournalEntry(
                assigned_object=sites[1],
                created_by=users[2],
                kind=JournalEntryKindChoices.KIND_WARNING,
                comments='foobar3'
            ),
            JournalEntry(
                assigned_object=racks[0],
                created_by=users[0],
                kind=JournalEntryKindChoices.KIND_INFO,
                comments='foobar4'
            ),
            JournalEntry(
                assigned_object=racks[0],
                created_by=users[1],
                kind=JournalEntryKindChoices.KIND_SUCCESS,
                comments='foobar5'
            ),
            JournalEntry(
                assigned_object=racks[1],
                created_by=users[2],
                kind=JournalEntryKindChoices.KIND_WARNING,
                comments='foobar6'
            ),
        )
        JournalEntry.objects.bulk_create(journal_entries)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_created_by(self):
        users = User.objects.filter(username__in=['Alice', 'Bob'])
        params = {'created_by': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'created_by_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_assigned_object_type(self):
        params = {'assigned_object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'assigned_object_type_id': [ContentType.objects.get(app_label='dcim', model='site').pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_assigned_object(self):
        params = {
            'assigned_object_type': 'dcim.site',
            'assigned_object_id': [Site.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_kind(self):
        params = {'kind': [JournalEntryKindChoices.KIND_INFO, JournalEntryKindChoices.KIND_SUCCESS]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_created(self):
        pk_list = self.queryset.values_list('pk', flat=True)[:2]
        self.queryset.filter(pk__in=pk_list).update(created=datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        params = {
            'created_after': '2020-12-31T00:00:00',
            'created_before': '2021-01-02T00:00:00',
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ConfigContextTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ConfigContext.objects.all()
    filterset = ConfigContextFilterSet
    ignore_fields = ('data', 'data_path')

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-3'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-4'),
        )
        DeviceType.objects.bulk_create(device_types)

        device_roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(device_roles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_types[0]),
            Cluster(name='Cluster 2', type=cluster_types[1]),
            Cluster(name='Cluster 3', type=cluster_types[2]),
        )
        Cluster.objects.bulk_create(clusters)

        tenant_groups = (
            TenantGroup(name='Tenant Group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant Group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant Group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        for i in range(0, 3):
            is_active = bool(i % 2)
            c = ConfigContext.objects.create(
                name=f"Config Context {i + 1}",
                is_active=is_active,
                data='{"foo": 123}',
                description=f"foobar{i + 1}"
            )
            c.regions.set([regions[i]])
            c.site_groups.set([site_groups[i]])
            c.sites.set([sites[i]])
            c.locations.set([locations[i]])
            c.device_types.set([device_types[i]])
            c.roles.set([device_roles[i]])
            c.platforms.set([platforms[i]])
            c.cluster_types.set([cluster_types[i]])
            c.cluster_groups.set([cluster_groups[i]])
            c.clusters.set([clusters[i]])
            c.tenant_groups.set([tenant_groups[i]])
            c.tenants.set([tenants[i]])
            c.tags.set([tags[i]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Config Context 1', 'Config Context 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_active(self):
        params = {'is_active': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'is_active': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_type(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_role(self):
        device_roles = DeviceRole.objects.all()[:2]
        params = {'device_role_id': [device_roles[0].pk, device_roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_role': [device_roles[0].slug, device_roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        platforms = Platform.objects.all()[:2]
        params = {'platform_id': [platforms[0].pk, platforms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'platform': [platforms[0].slug, platforms[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_group(self):
        cluster_groups = ClusterGroup.objects.all()[:2]
        params = {'cluster_group_id': [cluster_groups[0].pk, cluster_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_group': [cluster_groups[0].slug, cluster_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_type(self):
        cluster_types = ClusterType.objects.all()[:2]
        params = {'cluster_type_id': [cluster_types[0].pk, cluster_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_type': [cluster_types[0].slug, cluster_types[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster(self):
        clusters = Cluster.objects.all()[:2]
        params = {'cluster_id': [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tags(self):
        tags = Tag.objects.all()[:2]
        params = {'tag_id': [tags[0].pk, tags[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tag': [tags[0].slug, tags[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ConfigTemplateTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ConfigTemplate.objects.all()
    filterset = ConfigTemplateFilterSet
    ignore_fields = ('template_code', 'environment_params', 'data_path')

    @classmethod
    def setUpTestData(cls):
        config_templates = (
            ConfigTemplate(name='Config Template 1', template_code='TESTING', description='foobar1'),
            ConfigTemplate(name='Config Template 2', template_code='TESTING', description='foobar2'),
            ConfigTemplate(name='Config Template 3', template_code='TESTING'),
        )
        ConfigTemplate.objects.bulk_create(config_templates)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Config Template 1', 'Config Template 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class TagTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Tag.objects.all()
    filterset = TagFilterSet
    ignore_fields = (
        'object_types',

        # Reverse relationships (to tagged models) we can ignore
        'aggregate',
        'asn',
        'asnrange',
        'cable',
        'circuit',
        'circuitgroup',
        'circuitgroupassignment',
        'circuittermination',
        'circuittype',
        'cluster',
        'clustergroup',
        'clustertype',
        'configtemplate',
        'consoleport',
        'consoleserverport',
        'contact',
        'contactassignment',
        'contactgroup',
        'contactrole',
        'datasource',
        'device',
        'devicebay',
        'devicerole',
        'devicetype',
        'dummymodel',  # From dummy_plugin
        'dummynetboxmodel',  # From dummy_plugin
        'eventrule',
        'fhrpgroup',
        'frontport',
        'ikepolicy',
        'ikeproposal',
        'interface',
        'inventoryitem',
        'inventoryitemrole',
        'ipaddress',
        'iprange',
        'ipsecpolicy',
        'ipsecprofile',
        'ipsecproposal',
        'journalentry',
        'l2vpn',
        'l2vpntermination',
        'location',
        'macaddress',
        'manufacturer',
        'module',
        'modulebay',
        'moduletype',
        'platform',
        'powerfeed',
        'poweroutlet',
        'powerpanel',
        'powerport',
        'prefix',
        'provider',
        'provideraccount',
        'providernetwork',
        'rack',
        'rackreservation',
        'rackrole',
        'racktype',
        'rearport',
        'region',
        'rir',
        'role',
        'routetarget',
        'service',
        'servicetemplate',
        'site',
        'sitegroup',
        'tenant',
        'tenantgroup',
        'tunnel',
        'tunnelgroup',
        'tunneltermination',
        'virtualchassis',
        'virtualcircuit',
        'virtualcircuittermination',
        'virtualcircuittype',
        'virtualdevicecontext',
        'virtualdisk',
        'virtualmachine',
        'vlan',
        'vlangroup',
        'vlantranslationpolicy',
        'vlantranslationrule',
        'vminterface',
        'vrf',
        'webhook',
        'wirelesslan',
        'wirelesslangroup',
        'wirelesslink',
    )

    @classmethod
    def setUpTestData(cls):
        object_types = {
            'site': ObjectType.objects.get_by_natural_key('dcim', 'site'),
            'provider': ObjectType.objects.get_by_natural_key('circuits', 'provider'),
        }

        tags = (
            Tag(name='Tag 1', slug='tag-1', color='ff0000', description='foobar1'),
            Tag(name='Tag 2', slug='tag-2', color='00ff00', description='foobar2'),
            Tag(name='Tag 3', slug='tag-3', color='0000ff'),
        )
        Tag.objects.bulk_create(tags)
        tags[0].object_types.add(object_types['site'])
        tags[1].object_types.add(object_types['provider'])

        # Apply some tags so we can filter by content type
        site = Site.objects.create(name='Site 1', slug='site-1')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')

        site.tags.set([tags[0]])
        provider.tags.set([tags[1]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Tag 1', 'Tag 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['tag-1', 'tag-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_content_type(self):
        params = {'content_type': ['dcim.site', 'circuits.provider']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        site_ct = ContentType.objects.get_for_model(Site).pk
        provider_ct = ContentType.objects.get_for_model(Provider).pk
        params = {'content_type_id': [site_ct, provider_ct]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_types(self):
        params = {'for_object_type_id': [ObjectType.objects.get_by_natural_key('dcim', 'site').pk]}
        self.assertEqual(
            list(self.filterset(params, self.queryset).qs.values_list('name', flat=True)),
            ['Tag 1', 'Tag 3']
        )
        params = {'for_object_type_id': [ObjectType.objects.get_by_natural_key('circuits', 'provider').pk]}
        self.assertEqual(
            list(self.filterset(params, self.queryset).qs.values_list('name', flat=True)),
            ['Tag 2', 'Tag 3']
        )


class ChangeLoggedFilterSetTestCase(TestCase):
    """
    Evaluate base ChangeLoggedFilterSet filters using the Site model.
    """
    queryset = Site.objects.all()
    filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):
        content_type = ContentType.objects.get_for_model(Site)

        # Create three sites
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
            Site(name='Site 4', slug='site-4'),
        )
        Site.objects.bulk_create(sites)

        # Simulate *creation* changelog records for two of the sites
        request_id = uuid.uuid4()
        cls.create_request_id = request_id
        objectchanges = (
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[0].pk,
                action=ObjectChangeActionChoices.ACTION_CREATE,
                request_id=request_id
            ),
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[1].pk,
                action=ObjectChangeActionChoices.ACTION_CREATE,
                request_id=request_id
            ),
        )
        ObjectChange.objects.bulk_create(objectchanges)

        # Simulate *update* changelog records for two of the sites
        request_id = uuid.uuid4()
        cls.update_request_id = request_id
        objectchanges = (
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[0].pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                request_id=request_id
            ),
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[1].pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                request_id=request_id
            ),
        )
        ObjectChange.objects.bulk_create(objectchanges)

        # Simulate *create* and *update* changelog records for two of the sites
        request_id = uuid.uuid4()
        cls.create_update_request_id = request_id
        objectchanges = (
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[2].pk,
                action=ObjectChangeActionChoices.ACTION_CREATE,
                request_id=request_id
            ),
            ObjectChange(
                changed_object_type=content_type,
                changed_object_id=sites[3].pk,
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                request_id=request_id
            ),
        )
        ObjectChange.objects.bulk_create(objectchanges)

    def test_created_by_request(self):
        params = {'created_by_request': self.create_request_id}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        self.assertEqual(self.queryset.count(), 4)

    def test_updated_by_request(self):
        params = {'updated_by_request': self.update_request_id}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        self.assertEqual(self.queryset.count(), 4)

    def test_modified_by_request(self):
        params = {'modified_by_request': self.create_update_request_id}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        self.assertEqual(self.queryset.count(), 4)


class NotificationGroupTestCase(TestCase, BaseFilterSetTests):
    queryset = NotificationGroup.objects.all()
    filterset = NotificationGroupFilterSet

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

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        notification_groups = (
            NotificationGroup(name='Notification Group 1'),
            NotificationGroup(name='Notification Group 2'),
            NotificationGroup(name='Notification Group 3'),
        )
        NotificationGroup.objects.bulk_create(notification_groups)
        notification_groups[0].users.add(users[0])
        notification_groups[1].users.add(users[1])
        notification_groups[2].users.add(users[2])
        notification_groups[0].groups.add(groups[0])
        notification_groups[1].groups.add(groups[1])
        notification_groups[2].groups.add(groups[2])

    def test_user(self):
        users = User.objects.filter(username__startswith='User')
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = Group.objects.all()
        params = {'group': [groups[0].name, groups[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
