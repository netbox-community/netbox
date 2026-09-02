from django.test import TestCase

from core.events import OBJECT_CREATED
from core.models import ObjectType
from dcim.models import Site
from extras.choices import CustomFieldStatusChoices, CustomFieldTypeChoices
from extras.models import Bookmark, CustomField, EventRule, Notification, Subscription
from extras.tables import *
from utilities.testing import TableTestCases


class CustomFieldTableTestCase(TableTestCases.StandardTableTestCase):
    table = CustomFieldTable


class CustomFieldStatusColumnTestCase(TestCase):
    """
    A field which is not live must be distinguishable at a glance from one which is: deleting a
    field with a large amount of stored data reports success while leaving it listed until the purge
    job completes (see CustomFieldStatusColumn).
    """
    @classmethod
    def setUpTestData(cls):
        for status in (
            CustomFieldStatusChoices.STATUS_ACTIVE,
            CustomFieldStatusChoices.STATUS_PROVISIONING,
            CustomFieldStatusChoices.STATUS_DELETING,
        ):
            custom_field = CustomField.objects.create(
                name=f'field_{status}', type=CustomFieldTypeChoices.TYPE_TEXT
            )
            # Applied via the queryset to bypass the guard against modifying a pending field
            CustomField.objects.filter(pk=custom_field.pk).update(status=status)

    def _row(self, status):
        table = CustomFieldTable(CustomField.objects.filter(status=status))
        return table.rows[0]

    def test_status_is_shown_by_default(self):
        self.assertIn('status', CustomFieldTable.Meta.default_columns)

    def test_active_field_renders_a_green_checkmark(self):
        cell = self._row(CustomFieldStatusChoices.STATUS_ACTIVE).get_cell('status')

        self.assertInHTML(
            '<span class="badge text-bg-green" title="Active"><i class="mdi mdi-check-bold"></i></span>', cell
        )

    def test_pending_field_renders_an_orange_warning(self):
        for status, label in (
            (CustomFieldStatusChoices.STATUS_PROVISIONING, 'Provisioning'),
            (CustomFieldStatusChoices.STATUS_DELETING, 'Deleting'),
        ):
            with self.subTest(status=status):
                cell = self._row(status).get_cell('status')

                self.assertInHTML(
                    f'<span class="badge text-bg-orange" title="{label}">'
                    f'<i class="mdi mdi-alert"></i></span>',
                    cell
                )

    def test_export_records_the_label(self):
        """
        The icon carries no text, so an export must fall back to the human-readable status.
        """
        for status, label in (
            (CustomFieldStatusChoices.STATUS_ACTIVE, 'Active'),
            (CustomFieldStatusChoices.STATUS_PROVISIONING, 'Provisioning'),
            (CustomFieldStatusChoices.STATUS_DELETING, 'Deleting'),
        ):
            with self.subTest(status=status):
                self.assertEqual(self._row(status).get_cell_value('status'), label)


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
