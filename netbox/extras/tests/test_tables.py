from django.test import TestCase

from core.events import OBJECT_CREATED
from core.models import ObjectType
from dcim.models import Site
from extras.models import Bookmark, EventRule, Notification, Subscription
from extras.tables import *
from utilities.testing import TableTestCases


class CustomFieldTableTestCase(TableTestCases.StandardTableTestCase):
    table = CustomFieldTable


class CustomFieldChoiceSetTableTestCase(TableTestCases.StandardTableTestCase):
    table = CustomFieldChoiceSetTable


class CustomLinkTableTestCase(TableTestCases.StandardTableTestCase):
    table = CustomLinkTable


class ExportTemplateTableTestCase(TableTestCases.StandardTableTestCase):
    table = ExportTemplateTable


class SavedFilterTableTestCase(TableTestCases.StandardTableTestCase):
    table = SavedFilterTable


class TableConfigTableTestCase(TableTestCases.StandardTableTestCase):
    table = TableConfigTable


class BookmarkTableTestCase(TableTestCases.StandardTableTestCase):
    table = BookmarkTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Bookmark.objects.all()', Bookmark.objects.all()),
    ]


class NotificationGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = NotificationGroupTable


class NotificationTableTestCase(TableTestCases.StandardTableTestCase):
    table = NotificationTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Notification.objects.all()', Notification.objects.all()),
    ]


class SubscriptionTableTestCase(TableTestCases.StandardTableTestCase):
    table = SubscriptionTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Subscription.objects.all()', Subscription.objects.all()),
    ]


class WebhookTableTestCase(TableTestCases.StandardTableTestCase):
    table = WebhookTable


class EventRuleTableTestCase(TableTestCases.StandardTableTestCase):
    table = EventRuleTable


class EventRuleTableActionTypeRenderingTestCase(TestCase):
    """
    render_action_type() badges an unregistered action as unavailable; value_action_type() carries
    the same label for non-HTML output (e.g. CSV export), without the markup.
    """

    def test_render_action_type_for_registered_action(self):
        rule = EventRule.objects.create(name='Render Test Rule', event_types=[OBJECT_CREATED], action_type='webhook')
        rule.object_types.set([ObjectType.objects.get_for_model(Site)])

        table = EventRuleTable(EventRule.objects.filter(pk=rule.pk))
        self.assertEqual(table.render_action_type(rule), 'Webhook')
        self.assertEqual(table.value_action_type(rule), 'Webhook')

    def test_render_action_type_for_unregistered_action(self):
        rule = EventRule.objects.create(
            name='Render Test Unavailable Rule',
            event_types=[OBJECT_CREATED],
            action_type='someplugin.not_installed_render_test',
        )
        rule.object_types.set([ObjectType.objects.get_for_model(Site)])

        table = EventRuleTable(EventRule.objects.filter(pk=rule.pk))
        rendered = table.render_action_type(rule)
        self.assertIn('someplugin.not_installed_render_test (unavailable)', rendered)
        self.assertIn('badge text-bg-red', rendered)

        # The same label, without markup
        value = table.value_action_type(rule)
        self.assertEqual(value, 'someplugin.not_installed_render_test (unavailable)')
        self.assertNotIn('<span', value)


class TagTableTestCase(TableTestCases.StandardTableTestCase):
    table = TagTable


class ConfigContextProfileTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigContextProfileTable


class ConfigContextTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigContextTable


class ConfigTemplateTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigTemplateTable


class ImageAttachmentTableTestCase(TableTestCases.StandardTableTestCase):
    table = ImageAttachmentTable


class JournalEntryTableTestCase(TableTestCases.StandardTableTestCase):
    table = JournalEntryTable
