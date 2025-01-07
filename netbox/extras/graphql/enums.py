from enum import Enum
import strawberry

__all__ = [
    'CustomFieldTypeEnum',
    'CustomFieldFilterLogicEnum',
    'CustomFieldUIVisibleEnum',
    'CustomFieldUIEditableEnum',
    'CustomFieldChoiceSetBaseEnum',
    'CustomLinkButtonClassEnum',
    'BookmarkOrderingEnum',
    'JournalEntryKindEnum',
    'LogLevelEnum',
    'DurationEnum',
    'WebhookHttpMethodEnum',
    'ChangeActionEnum',
    'DashboardWidgetColorEnum',
    'EventRuleActionEnum',
]

#
# CustomFields
#


@strawberry.enum
class CustomFieldTypeEnum(Enum):
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


@strawberry.enum
class CustomFieldFilterLogicEnum(Enum):
    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'


@strawberry.enum
class CustomFieldUIVisibleEnum(Enum):
    ALWAYS = 'always'
    IF_SET = 'if-set'
    HIDDEN = 'hidden'


@strawberry.enum
class CustomFieldUIEditableEnum(Enum):
    YES = 'yes'
    NO = 'no'
    HIDDEN = 'hidden'


@strawberry.enum
class CustomFieldChoiceSetBaseEnum(Enum):
    IATA = 'IATA'
    ISO_3166 = 'ISO_3166'
    UN_LOCODE = 'UN_LOCODE'


#
# CustomLinks
#


@strawberry.enum
class CustomLinkButtonClassEnum(Enum):
    LINK = 'ghost-dark'


#
# Bookmarks
#


@strawberry.enum
class BookmarkOrderingEnum(Enum):
    ORDERING_NEWEST = '-created'
    ORDERING_OLDEST = 'created'
    ORDERING_ALPHABETICAL_AZ = 'name'
    ORDERING_ALPHABETICAL_ZA = '-name'


#
# Journal entries
#


@strawberry.enum
class JournalEntryKindEnum(Enum):
    key = 'JournalEntry.kind'

    KIND_INFO = 'info'
    KIND_SUCCESS = 'success'
    KIND_WARNING = 'warning'
    KIND_DANGER = 'danger'


#
# Reports and Scripts
#


@strawberry.enum
class LogLevelEnum(Enum):
    LOG_DEBUG = 'debug'
    LOG_DEFAULT = 'default'
    LOG_INFO = 'info'
    LOG_SUCCESS = 'success'
    LOG_WARNING = 'warning'
    LOG_FAILURE = 'failure'


@strawberry.enum
class DurationEnum(Enum):
    HOURLY = 60
    TWELVE_HOURS = 720
    DAILY = 1440
    WEEKLY = 10080
    THIRTY_DAYS = 43200


#
# Webhooks
#


@strawberry.enum
class WebhookHttpMethodEnum(Enum):
    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_PATCH = 'PATCH'
    METHOD_DELETE = 'DELETE'


#
# Staging
#


@strawberry.enum
class ChangeActionEnum(Enum):
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'


#
# Dashboard widgets
#


@strawberry.enum
class DashboardWidgetColorEnum(Enum):
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


#
# Event Rules
#


@strawberry.enum
class EventRuleActionEnum(Enum):
    WEBHOOK = 'webhook'
    SCRIPT = 'script'
    NOTIFICATION = 'notification'
