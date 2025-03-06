import logging

from django.utils.translation import gettext_lazy as _

from netbox.choices import ButtonColorChoices
from utilities.choices import ChoiceSet


#
# CustomFields
#

class CustomFieldTypeChoices(ChoiceSet):

    TYPE_TEXT = 'text'
    TYPE_LONGTEXT = 'longtext'
    TYPE_INTEGER = 'integer'
    TYPE_DECIMAL = 'decimal'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_DATETIME = 'datetime'
    TYPE_URL = 'url'
    TYPE_JSON = 'json'
    TYPE_SELECT = 'select'
    TYPE_MULTISELECT = 'multiselect'
    TYPE_OBJECT = 'object'
    TYPE_MULTIOBJECT = 'multiobject'

    CHOICES = (
        (TYPE_TEXT, _('Text')),
        (TYPE_LONGTEXT, _('Text (long)')),
        (TYPE_INTEGER, _('Integer')),
        (TYPE_DECIMAL, _('Decimal')),
        (TYPE_BOOLEAN, _('Boolean (true/false)')),
        (TYPE_DATE, _('Date')),
        (TYPE_DATETIME, _('Date & time')),
        (TYPE_URL, _('URL')),
        (TYPE_JSON, _('JSON')),
        (TYPE_SELECT, _('Selection')),
        (TYPE_MULTISELECT, _('Multiple selection')),
        (TYPE_OBJECT, _('Object')),
        (TYPE_MULTIOBJECT, _('Multiple objects')),
    )


class CustomFieldFilterLogicChoices(ChoiceSet):

    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'

    CHOICES = (
        (FILTER_DISABLED, _('Disabled')),
        (FILTER_LOOSE, _('Loose')),
        (FILTER_EXACT, _('Exact')),
    )


class CustomFieldUIVisibleChoices(ChoiceSet):

    ALWAYS = 'always'
    IF_SET = 'if-set'
    HIDDEN = 'hidden'

    CHOICES = (
        (ALWAYS, _('Always'), 'green'),
        (IF_SET, _('If set'), 'yellow'),
        (HIDDEN, _('Hidden'), 'gray'),
    )


class CustomFieldUIEditableChoices(ChoiceSet):

    YES = 'yes'
    NO = 'no'
    HIDDEN = 'hidden'

    CHOICES = (
        (YES, _('Yes'), 'green'),
        (NO, _('No'), 'red'),
        (HIDDEN, _('Hidden'), 'gray'),
    )


class CustomFieldChoiceSetBaseChoices(ChoiceSet):

    IATA = 'IATA'
    ISO_3166 = 'ISO_3166'
    UN_LOCODE = 'UN_LOCODE'

    CHOICES = (
        (IATA, 'IATA (Airport codes)'),
        (ISO_3166, 'ISO 3166 (Country codes)'),
        (UN_LOCODE, 'UN/LOCODE (Location codes)'),
    )


#
# CustomLinks
#

class CustomLinkButtonClassChoices(ButtonColorChoices):

    LINK = 'ghost-dark'

    CHOICES = (
        *ButtonColorChoices.CHOICES,
        (LINK, _('Link')),
    )


#
# Bookmarks
#

class BookmarkOrderingChoices(ChoiceSet):

    ORDERING_NEWEST = '-created'
    ORDERING_OLDEST = 'created'
    ORDERING_ALPHABETICAL_AZ = 'name'
    ORDERING_ALPHABETICAL_ZA = '-name'

    CHOICES = (
        (ORDERING_NEWEST, _('Newest')),
        (ORDERING_OLDEST, _('Oldest')),
        (ORDERING_ALPHABETICAL_AZ, _('Alphabetical (A-Z)')),
        (ORDERING_ALPHABETICAL_ZA, _('Alphabetical (Z-A)')),
    )


#
# Journal entries
#

class JournalEntryKindChoices(ChoiceSet):
    key = 'JournalEntry.kind'

    KIND_INFO = 'info'
    KIND_SUCCESS = 'success'
    KIND_WARNING = 'warning'
    KIND_DANGER = 'danger'

    CHOICES = [
        (KIND_INFO, _('Info'), 'cyan'),
        (KIND_SUCCESS, _('Success'), 'green'),
        (KIND_WARNING, _('Warning'), 'yellow'),
        (KIND_DANGER, _('Danger'), 'red'),
    ]


#
# Reports and Scripts
#

class LogLevelChoices(ChoiceSet):

    LOG_DEBUG = 'debug'
    LOG_DEFAULT = 'default'
    LOG_INFO = 'info'
    LOG_SUCCESS = 'success'
    LOG_WARNING = 'warning'
    LOG_FAILURE = 'failure'

    CHOICES = (
        (LOG_DEBUG, _('Debug'), 'teal'),
        (LOG_DEFAULT, _('Default'), 'gray'),
        (LOG_INFO, _('Info'), 'cyan'),
        (LOG_SUCCESS, _('Success'), 'green'),
        (LOG_WARNING, _('Warning'), 'yellow'),
        (LOG_FAILURE, _('Failure'), 'red'),
    )

    SYSTEM_LEVELS = {
        LOG_DEBUG: logging.DEBUG,
        LOG_DEFAULT: logging.INFO,
        LOG_INFO: logging.INFO,
        LOG_SUCCESS: logging.INFO,
        LOG_WARNING: logging.WARNING,
        LOG_FAILURE: logging.ERROR,
    }


class DurationChoices(ChoiceSet):

    CHOICES = (
        (60, _('Hourly')),
        (720, _('12 hours')),
        (1440, _('Daily')),
        (10080, _('Weekly')),
        (43200, _('30 days')),
    )


#
# Webhooks
#

class WebhookHttpMethodChoices(ChoiceSet):

    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_PATCH = 'PATCH'
    METHOD_DELETE = 'DELETE'

    CHOICES = (
        (METHOD_GET, 'GET'),
        (METHOD_POST, 'POST'),
        (METHOD_PUT, 'PUT'),
        (METHOD_PATCH, 'PATCH'),
        (METHOD_DELETE, 'DELETE'),
    )


#
# Staging
#

class ChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        (ACTION_CREATE, _('Create'), 'green'),
        (ACTION_UPDATE, _('Update'), 'blue'),
        (ACTION_DELETE, _('Delete'), 'red'),
    )


#
# Dashboard widgets
#

class DashboardWidgetColorChoices(ChoiceSet):
    BLUE = 'blue'
    INDIGO = 'indigo'
    PURPLE = 'purple'
    PINK = 'pink'
    RED = 'red'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    GREEN = 'green'
    TEAL = 'teal'
    CYAN = 'cyan'
    GRAY = 'gray'
    BLACK = 'black'
    WHITE = 'white'

    CHOICES = (
        (BLUE, _('Blue')),
        (INDIGO, _('Indigo')),
        (PURPLE, _('Purple')),
        (PINK, _('Pink')),
        (RED, _('Red')),
        (ORANGE, _('Orange')),
        (YELLOW, _('Yellow')),
        (GREEN, _('Green')),
        (TEAL, _('Teal')),
        (CYAN, _('Cyan')),
        (GRAY, _('Gray')),
        (BLACK, _('Black')),
        (WHITE, _('White')),
    )


#
# Event Rules
#

class EventRuleActionChoices(ChoiceSet):

    WEBHOOK = 'webhook'
    SCRIPT = 'script'
    NOTIFICATION = 'notification'

    CHOICES = (
        (WEBHOOK, _('Webhook')),
        (SCRIPT, _('Script')),
        (NOTIFICATION, _('Notification')),
    )
