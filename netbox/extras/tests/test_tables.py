from extras.models import Bookmark, Notification, Subscription
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
