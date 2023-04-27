from utilities.choices import ButtonColorChoices, ChoiceSet


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
        (TYPE_TEXT, 'Text'),
        (TYPE_LONGTEXT, 'Text (long)'),
        (TYPE_INTEGER, 'Integer'),
        (TYPE_DECIMAL, 'Decimal'),
        (TYPE_BOOLEAN, 'Boolean (true/false)'),
        (TYPE_DATE, 'Date'),
        (TYPE_DATETIME, 'Date & time'),
        (TYPE_URL, 'URL'),
        (TYPE_JSON, 'JSON'),
        (TYPE_SELECT, 'Selection'),
        (TYPE_MULTISELECT, 'Multiple selection'),
        (TYPE_OBJECT, 'Object'),
        (TYPE_MULTIOBJECT, 'Multiple objects'),
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


class CustomFieldVisibilityChoices(ChoiceSet):

    VISIBILITY_READ_WRITE = 'read-write'
    VISIBILITY_READ_ONLY = 'read-only'
    VISIBILITY_HIDDEN = 'hidden'

    CHOICES = (
        (VISIBILITY_READ_WRITE, 'Read/Write'),
        (VISIBILITY_READ_ONLY, 'Read-only'),
        (VISIBILITY_HIDDEN, 'Hidden'),
    )


#
# CustomLinks
#

class CustomLinkButtonClassChoices(ButtonColorChoices):

    LINK = 'ghost-dark'

    CHOICES = (
        *ButtonColorChoices.CHOICES,
        (LINK, 'Link'),
    )

#
# ObjectChanges
#


class ObjectChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        (ACTION_CREATE, 'Created', 'green'),
        (ACTION_UPDATE, 'Updated', 'blue'),
        (ACTION_DELETE, 'Deleted', 'red'),
    )


#
# Jounral entries
#

class JournalEntryKindChoices(ChoiceSet):
    key = 'JournalEntry.kind'

    KIND_INFO = 'info'
    KIND_SUCCESS = 'success'
    KIND_WARNING = 'warning'
    KIND_DANGER = 'danger'

    CHOICES = [
        (KIND_INFO, 'Info', 'cyan'),
        (KIND_SUCCESS, 'Success', 'green'),
        (KIND_WARNING, 'Warning', 'yellow'),
        (KIND_DANGER, 'Danger', 'red'),
    ]


#
# Reports and Scripts
#

class LogLevelChoices(ChoiceSet):

    LOG_DEFAULT = 'default'
    LOG_SUCCESS = 'success'
    LOG_INFO = 'info'
    LOG_WARNING = 'warning'
    LOG_FAILURE = 'failure'

    CHOICES = (
        (LOG_DEFAULT, 'Default', 'gray'),
        (LOG_SUCCESS, 'Success', 'green'),
        (LOG_INFO, 'Info', 'cyan'),
        (LOG_WARNING, 'Warning', 'yellow'),
        (LOG_FAILURE, 'Failure', 'red'),
    )


class DurationChoices(ChoiceSet):

    CHOICES = (
        (60, 'Hourly'),
        (720, '12 hours'),
        (1440, 'Daily'),
        (10080, 'Weekly'),
        (43200, '30 days'),
    )


#
# Job results
#

class JobResultStatusChoices(ChoiceSet):

    STATUS_PENDING = 'pending'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_ERRORED = 'errored'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_PENDING, 'Pending', 'cyan'),
        (STATUS_SCHEDULED, 'Scheduled', 'gray'),
        (STATUS_RUNNING, 'Running', 'blue'),
        (STATUS_COMPLETED, 'Completed', 'green'),
        (STATUS_ERRORED, 'Errored', 'red'),
        (STATUS_FAILED, 'Failed', 'red'),
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


#
# Staging
#

class ChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
    )
