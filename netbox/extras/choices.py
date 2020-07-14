from utilities.choices import ChoiceSet


#
# CustomFields
#

class CustomFieldTypeChoices(ChoiceSet):

    TYPE_TEXT = 'text'
    TYPE_INTEGER = 'integer'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_URL = 'url'
    TYPE_SELECT = 'select'

    CHOICES = (
        (TYPE_TEXT, 'Text'),
        (TYPE_INTEGER, 'Integer'),
        (TYPE_BOOLEAN, 'Boolean (true/false)'),
        (TYPE_DATE, 'Date'),
        (TYPE_URL, 'URL'),
        (TYPE_SELECT, 'Selection'),
    )

    LEGACY_MAP = {
        TYPE_TEXT: 100,
        TYPE_INTEGER: 200,
        TYPE_BOOLEAN: 300,
        TYPE_DATE: 400,
        TYPE_URL: 500,
        TYPE_SELECT: 600,
    }


class CustomFieldFilterLogicChoices(ChoiceSet):

    FILTER_DISABLED = 'disabled'
    FILTER_LOOSE = 'loose'
    FILTER_EXACT = 'exact'

    CHOICES = (
        (FILTER_DISABLED, 'Disabled'),
        (FILTER_LOOSE, 'Loose'),
        (FILTER_EXACT, 'Exact'),
    )

    LEGACY_MAP = {
        FILTER_DISABLED: 0,
        FILTER_LOOSE: 1,
        FILTER_EXACT: 2,
    }


#
# CustomLinks
#

class CustomLinkButtonClassChoices(ChoiceSet):

    CLASS_DEFAULT = 'default'
    CLASS_PRIMARY = 'primary'
    CLASS_SUCCESS = 'success'
    CLASS_INFO = 'info'
    CLASS_WARNING = 'warning'
    CLASS_DANGER = 'danger'
    CLASS_LINK = 'link'

    CHOICES = (
        (CLASS_DEFAULT, 'Default'),
        (CLASS_PRIMARY, 'Primary (blue)'),
        (CLASS_SUCCESS, 'Success (green)'),
        (CLASS_INFO, 'Info (aqua)'),
        (CLASS_WARNING, 'Warning (orange)'),
        (CLASS_DANGER, 'Danger (red)'),
        (CLASS_LINK, 'None (link)'),
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

    LEGACY_MAP = {
        ACTION_CREATE: 1,
        ACTION_UPDATE: 2,
        ACTION_DELETE: 3,
    }


#
# ExportTemplates
#

class TemplateLanguageChoices(ChoiceSet):

    LANGUAGE_DJANGO = 'django'
    LANGUAGE_JINJA2 = 'jinja2'

    CHOICES = (
        (LANGUAGE_DJANGO, 'Django'),
        (LANGUAGE_JINJA2, 'Jinja2'),
    )

    LEGACY_MAP = {
        LANGUAGE_DJANGO: 10,
        LANGUAGE_JINJA2: 20,
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

    CLASS_MAP = (
        (LOG_DEFAULT, 'default'),
        (LOG_SUCCESS, 'success'),
        (LOG_INFO, 'info'),
        (LOG_WARNING, 'warning'),
        (LOG_FAILURE, 'danger'),
    )

    LEGACY_MAP = (
        (LOG_DEFAULT, 0),
        (LOG_SUCCESS, 10),
        (LOG_INFO, 20),
        (LOG_WARNING, 30),
        (LOG_FAILURE, 40),
    )


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
