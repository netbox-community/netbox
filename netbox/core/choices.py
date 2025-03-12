from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


#
# Data sources
#

class DataSourceStatusChoices(ChoiceSet):
    NEW = 'new'
    QUEUED = 'queued'
    SYNCING = 'syncing'
    COMPLETED = 'completed'
    FAILED = 'failed'

    CHOICES = (
        (NEW, _('New'), 'blue'),
        (QUEUED, _('Queued'), 'orange'),
        (SYNCING, _('Syncing'), 'cyan'),
        (COMPLETED, _('Completed'), 'green'),
        (FAILED, _('Failed'), 'red'),
    )


#
# Managed files
#

class ManagedFileRootPathChoices(ChoiceSet):
    SCRIPTS = 'scripts'  # settings.SCRIPTS_ROOT
    REPORTS = 'reports'  # settings.REPORTS_ROOT

    CHOICES = (
        (SCRIPTS, _('Scripts')),
        (REPORTS, _('Reports')),
    )


#
# Jobs
#

class JobStatusChoices(ChoiceSet):

    STATUS_PENDING = 'pending'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_ERRORED = 'errored'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_PENDING, _('Pending'), 'cyan'),
        (STATUS_SCHEDULED, _('Scheduled'), 'gray'),
        (STATUS_RUNNING, _('Running'), 'blue'),
        (STATUS_COMPLETED, _('Completed'), 'green'),
        (STATUS_ERRORED, _('Errored'), 'red'),
        (STATUS_FAILED, _('Failed'), 'red'),
    )

    ENQUEUED_STATE_CHOICES = (
        STATUS_PENDING,
        STATUS_SCHEDULED,
        STATUS_RUNNING,
    )

    TERMINAL_STATE_CHOICES = (
        STATUS_COMPLETED,
        STATUS_ERRORED,
        STATUS_FAILED,
    )


class JobIntervalChoices(ChoiceSet):
    INTERVAL_MINUTELY = 1
    INTERVAL_HOURLY = 60
    INTERVAL_DAILY = 60 * 24
    INTERVAL_WEEKLY = 60 * 24 * 7

    CHOICES = (
        (INTERVAL_MINUTELY, _('Minutely')),
        (INTERVAL_HOURLY, _('Hourly')),
        (INTERVAL_HOURLY * 12, _('12 hours')),
        (INTERVAL_DAILY, _('Daily')),
        (INTERVAL_WEEKLY, _('Weekly')),
        (INTERVAL_DAILY * 30, _('30 days')),
    )


#
# ObjectChanges
#

class ObjectChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        (ACTION_CREATE, _('Created'), 'green'),
        (ACTION_UPDATE, _('Updated'), 'blue'),
        (ACTION_DELETE, _('Deleted'), 'red'),
    )
