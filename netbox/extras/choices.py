import logging

from django.utils.translation import gettext_lazy as _

from netbox.choices import ButtonColorChoices
from utilities.choices import Choice, ChoiceSet

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
        Choice(TYPE_TEXT, _('Text'), description=_('A single line of text')),
        Choice(TYPE_LONGTEXT, _('Text (long)'), description=_('Multi-line text with Markdown support')),
        Choice(TYPE_INTEGER, _('Integer'), description=_('A whole number (positive or negative)')),
        Choice(TYPE_DECIMAL, _('Decimal'), description=_('A fixed-precision decimal number')),
        Choice(TYPE_BOOLEAN, _('Boolean'), description=_('A true or false value')),
        Choice(TYPE_DATE, _('Date'), description=_('A calendar date')),
        Choice(TYPE_DATETIME, _('Date & time'), description=_('A calendar date and time')),
        Choice(TYPE_URL, _('URL'), description=_('A hyperlink to an external resource')),
        Choice(TYPE_JSON, _('JSON'), description=_('Arbitrary data encoded as JSON')),
        Choice(TYPE_SELECT, _('Selection'), description=_('A single value chosen from a predefined list')),
        Choice(
            TYPE_MULTISELECT,
            _('Multiple selection'),
            description=_('One or more values chosen from a predefined list')
        ),
        Choice(TYPE_OBJECT, _('Object'), description=_('A reference to a single NetBox object')),
        Choice(TYPE_MULTIOBJECT, _('Multiple objects'), description=_('References to one or more NetBox objects')),
    )


class CustomFieldFilterLogicChoices(ChoiceSet):

    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'

    CHOICES = (
        Choice(FILTER_DISABLED, _('Disabled'), description=_('The field cannot be used for filtering')),
        Choice(FILTER_LOOSE, _('Loose'), description=_('Match on a partial value (case-insensitive substring)')),
        Choice(FILTER_EXACT, _('Exact'), description=_('Match on the exact value')),
    )


class CustomFieldUIVisibleChoices(ChoiceSet):

    ALWAYS = 'always'
    IF_SET = 'if-set'
    HIDDEN = 'hidden'

    CHOICES = (
        Choice(ALWAYS, _('Always'), color='green', description=_('Always display the field')),
        Choice(IF_SET, _('If set'), color='yellow', description=_('Display the field only if it has a value')),
        Choice(HIDDEN, _('Hidden'), color='gray', description=_('Never display the field')),
    )


class CustomFieldUIEditableChoices(ChoiceSet):

    YES = 'yes'
    NO = 'no'
    HIDDEN = 'hidden'

    CHOICES = (
        Choice(YES, _('Yes'), color='green', description=_('The field value can be edited by users')),
        Choice(NO, _('No'), color='red', description=_('The field is displayed but cannot be edited')),
        Choice(HIDDEN, _('Hidden'), color='gray', description=_('The field is neither displayed nor editable')),
    )


class CustomFieldChoiceSetBaseChoices(ChoiceSet):

    IATA = 'IATA'
    ISO_3166 = 'ISO_3166'
    UN_LOCODE = 'UN_LOCODE'

    CHOICES = (
        Choice(IATA, 'IATA (Airport codes)'),
        Choice(ISO_3166, 'ISO 3166 (Country codes)'),
        Choice(UN_LOCODE, 'UN/LOCODE (Location codes)'),
    )


class CustomFieldChoiceColorChoices(ChoiceSet):

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
        Choice(BLUE, _('Blue'), color=BLUE),
        Choice(INDIGO, _('Indigo'), color=INDIGO),
        Choice(PURPLE, _('Purple'), color=PURPLE),
        Choice(PINK, _('Pink'), color=PINK),
        Choice(RED, _('Red'), color=RED),
        Choice(ORANGE, _('Orange'), color=ORANGE),
        Choice(YELLOW, _('Yellow'), color=YELLOW),
        Choice(GREEN, _('Green'), color=GREEN),
        Choice(TEAL, _('Teal'), color=TEAL),
        Choice(CYAN, _('Cyan'), color=CYAN),
        Choice(GRAY, _('Gray'), color=GRAY),
        Choice(BLACK, _('Black'), color=BLACK),
        Choice(WHITE, _('White'), color=WHITE),
    )


#
# CustomLinks
#

class CustomLinkButtonClassChoices(ButtonColorChoices):

    LINK = 'ghost-dark'

    CHOICES = (
        *ButtonColorChoices.CHOICES,
        Choice(LINK, _('Link'), description=_('Render the button as a borderless text link')),
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
        Choice(ORDERING_NEWEST, _('Newest')),
        Choice(ORDERING_OLDEST, _('Oldest')),
        Choice(ORDERING_ALPHABETICAL_AZ, _('Alphabetical (A-Z)')),
        Choice(ORDERING_ALPHABETICAL_ZA, _('Alphabetical (Z-A)')),
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
        Choice(KIND_INFO, _('Info'), color='cyan', description=_('An informational entry')),
        Choice(KIND_SUCCESS, _('Success'), color='green', description=_('A record of a successful outcome')),
        Choice(KIND_WARNING, _('Warning'), color='yellow', description=_('A cautionary note requiring attention')),
        Choice(KIND_DANGER, _('Danger'), color='red', description=_('A record of a critical issue or failure')),
    ]


#
# Reports and Scripts
#

class LogLevelChoices(ChoiceSet):

    LOG_DEBUG = 'debug'
    LOG_INFO = 'info'
    LOG_SUCCESS = 'success'
    LOG_WARNING = 'warning'
    LOG_FAILURE = 'failure'

    CHOICES = (
        Choice(LOG_DEBUG, _('Debug'), color='teal'),
        Choice(LOG_INFO, _('Info'), color='cyan'),
        Choice(LOG_SUCCESS, _('Success'), color='green'),
        Choice(LOG_WARNING, _('Warning'), color='yellow'),
        Choice(LOG_FAILURE, _('Failure'), color='red'),

    )

    SYSTEM_LEVELS = {
        LOG_DEBUG: logging.DEBUG,
        LOG_INFO: logging.INFO,
        LOG_SUCCESS: logging.INFO,
        LOG_WARNING: logging.WARNING,
        LOG_FAILURE: logging.ERROR,
    }


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
        Choice(METHOD_GET, 'GET'),
        Choice(METHOD_POST, 'POST'),
        Choice(METHOD_PUT, 'PUT'),
        Choice(METHOD_PATCH, 'PATCH'),
        Choice(METHOD_DELETE, 'DELETE'),
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
        Choice(BLUE, _('Blue')),
        Choice(INDIGO, _('Indigo')),
        Choice(PURPLE, _('Purple')),
        Choice(PINK, _('Pink')),
        Choice(RED, _('Red')),
        Choice(ORANGE, _('Orange')),
        Choice(YELLOW, _('Yellow')),
        Choice(GREEN, _('Green')),
        Choice(TEAL, _('Teal')),
        Choice(CYAN, _('Cyan')),
        Choice(GRAY, _('Gray')),
        Choice(BLACK, _('Black')),
        Choice(WHITE, _('White')),
    )


#
# Event Rules
#

class EventRuleActionChoices(ChoiceSet):

    WEBHOOK = 'webhook'
    SCRIPT = 'script'
    NOTIFICATION = 'notification'

    CHOICES = (
        Choice(WEBHOOK, _('Webhook'), description=_('Send an outgoing HTTP request to a remote endpoint')),
        Choice(SCRIPT, _('Script'), description=_('Execute a custom script')),
        Choice(
            NOTIFICATION,
            _('Notification'),
            description=_('Generate a notification for one or more users or groups')
        ),
    )
