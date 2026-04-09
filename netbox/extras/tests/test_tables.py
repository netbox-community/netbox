from extras.models import Bookmark, Notification, Subscription
from extras.tables import *
from utilities.testing import TableTestCases


class CustomFieldTableTest(TableTestCases.StandardTableTestCase):
    table = CustomFieldTable


class CustomFieldChoiceSetTableTest(TableTestCases.StandardTableTestCase):
    table = CustomFieldChoiceSetTable


class CustomLinkTableTest(TableTestCases.StandardTableTestCase):
    table = CustomLinkTable


class ExportTemplateTableTest(TableTestCases.StandardTableTestCase):
    table = ExportTemplateTable


class SavedFilterTableTest(TableTestCases.StandardTableTestCase):
    table = SavedFilterTable


class TableConfigTableTest(TableTestCases.StandardTableTestCase):
    table = TableConfigTable


class BookmarkTableTest(TableTestCases.StandardTableTestCase):
    table = BookmarkTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Bookmark.objects.all()', Bookmark.objects.all()),
    ]


class NotificationGroupTableTest(TableTestCases.StandardTableTestCase):
    table = NotificationGroupTable


class NotificationTableTest(TableTestCases.StandardTableTestCase):
    table = NotificationTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Notification.objects.all()', Notification.objects.all()),
    ]


class SubscriptionTableTest(TableTestCases.StandardTableTestCase):
    table = SubscriptionTable

    # The list view for this table lives in account.views (not extras.views),
    # so auto-discovery cannot find it. Provide an explicit queryset source.
    queryset_sources = [
        ('Subscription.objects.all()', Subscription.objects.all()),
    ]


class WebhookTableTest(TableTestCases.StandardTableTestCase):
    table = WebhookTable


class EventRuleTableTest(TableTestCases.StandardTableTestCase):
    table = EventRuleTable


class TagTableTest(TableTestCases.StandardTableTestCase):
    table = TagTable


class ConfigContextProfileTableTest(TableTestCases.StandardTableTestCase):
    table = ConfigContextProfileTable


class ConfigContextTableTest(TableTestCases.StandardTableTestCase):
    table = ConfigContextTable


class ConfigTemplateTableTest(TableTestCases.StandardTableTestCase):
    table = ConfigTemplateTable


class ImageAttachmentTableTest(TableTestCases.StandardTableTestCase):
    table = ImageAttachmentTable


class JournalEntryTableTest(TableTestCases.StandardTableTestCase):
    table = JournalEntryTable
