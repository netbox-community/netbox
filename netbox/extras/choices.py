from utilities.choices import ChoiceSet


#
# CustomFields
#

class CustomFieldTypeChoices(ChoiceSet):

    TYPE_TEXT = 'text'
    TYPE_LONGTEXT = 'longtext'
    TYPE_INTEGER = 'integer'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_URL = 'url'
    TYPE_SELECT = 'select'
    TYPE_MULTISELECT = 'multiselect'

    CHOICES = (
        (TYPE_TEXT, 'Text'),
        (TYPE_LONGTEXT, 'Text (long)'),
        (TYPE_INTEGER, 'Integer'),
        (TYPE_BOOLEAN, 'Boolean (true/false)'),
        (TYPE_DATE, 'Date'),
        (TYPE_URL, 'URL'),
        (TYPE_SELECT, 'Selection'),
        (TYPE_MULTISELECT, 'Multiple selection'),
    )


class CustomFieldFilterLogicChoices(ChoiceSet):

    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'

    CHOICES = (
        (FILTER_DISABLED, 'Disabled'),
        (FILTER_LOOSE, 'Loose'),
        (FILTER_EXACT, 'Exact'),
    )


#
# CustomLinks
#

class CustomLinkButtonClassChoices(ChoiceSet):

    CLASS_DEFAULT = 'outline-dark'
    CLASS_LINK = 'ghost-dark'
    CLASS_BLUE = 'blue'
    CLASS_INDIGO = 'indigo'
    CLASS_PURPLE = 'purple'
    CLASS_PINK = 'pink'
    CLASS_RED = 'red'
    CLASS_ORANGE = 'orange'
    CLASS_YELLOW = 'yellow'
    CLASS_GREEN = 'green'
    CLASS_TEAL = 'teal'
    CLASS_CYAN = 'cyan'
    CLASS_GRAY = 'secondary'

    CHOICES = (
        (CLASS_DEFAULT, 'Default'),
        (CLASS_LINK, 'Link'),
        (CLASS_BLUE, 'Blue'),
        (CLASS_INDIGO, 'Indigo'),
        (CLASS_PURPLE, 'Purple'),
        (CLASS_PINK, 'Pink'),
        (CLASS_RED, 'Red'),
        (CLASS_ORANGE, 'Orange'),
        (CLASS_YELLOW, 'Yellow'),
        (CLASS_GREEN, 'Green'),
        (CLASS_TEAL, 'Teal'),
        (CLASS_CYAN, 'Cyan'),
        (CLASS_GRAY, 'Gray'),
    )

#
# ObjectChanges
#


class ObjectChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        (ACTION_CREATE, 'Created'),
        (ACTION_UPDATE, 'Updated'),
        (ACTION_DELETE, 'Deleted'),
    )

    CSS_CLASSES = {
        ACTION_CREATE: 'success',
        ACTION_UPDATE: 'primary',
        ACTION_DELETE: 'danger',
    }


#
# Jounral entries
#

class JournalEntryKindChoices(ChoiceSet):

    KIND_INFO = 'info'
    KIND_SUCCESS = 'success'
    KIND_WARNING = 'warning'
    KIND_DANGER = 'danger'

    CHOICES = (
        (KIND_INFO, 'Info'),
        (KIND_SUCCESS, 'Success'),
        (KIND_WARNING, 'Warning'),
        (KIND_DANGER, 'Danger'),
    )

    CSS_CLASSES = {
        KIND_INFO: 'info',
        KIND_SUCCESS: 'success',
        KIND_WARNING: 'warning',
        KIND_DANGER: 'danger',
    }


#
# Log Levels for Reports and Scripts
#

class LogLevelChoices(ChoiceSet):

    LOG_DEFAULT = 'default'
    LOG_SUCCESS = 'success'
    LOG_INFO = 'info'
    LOG_WARNING = 'warning'
    LOG_FAILURE = 'failure'

    CHOICES = (
        (LOG_DEFAULT, 'Default'),
        (LOG_SUCCESS, 'Success'),
        (LOG_INFO, 'Info'),
        (LOG_WARNING, 'Warning'),
        (LOG_FAILURE, 'Failure'),
    )

    CSS_CLASSES = {
        LOG_DEFAULT: 'secondary',
        LOG_SUCCESS: 'success',
        LOG_INFO: 'info',
        LOG_WARNING: 'warning',
        LOG_FAILURE: 'danger',
    }


#
# Job results
#

class JobResultStatusChoices(ChoiceSet):

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_ERRORED = 'errored'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ERRORED, 'Errored'),
        (STATUS_FAILED, 'Failed'),
    )

    TERMINAL_STATE_CHOICES = (
        STATUS_COMPLETED,
        STATUS_ERRORED,
        STATUS_FAILED,
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
