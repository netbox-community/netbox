from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

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
        Choice(NEW, _('New'), color='blue', description=_('Newly created and not yet synchronized')),
        Choice(QUEUED, _('Queued'), color='orange', description=_('Queued for synchronization')),
        Choice(SYNCING, _('Syncing'), color='cyan', description=_('Synchronization in progress')),
        Choice(COMPLETED, _('Completed'), color='green', description=_('Most recent synchronization succeeded')),
        Choice(FAILED, _('Failed'), color='red', description=_('Most recent synchronization failed')),
    )


#
# Managed files
#

class ManagedFileRootPathChoices(ChoiceSet):
    SCRIPTS = 'scripts'  # settings.SCRIPTS_ROOT
    REPORTS = 'reports'  # settings.REPORTS_ROOT

    CHOICES = (
        Choice(SCRIPTS, _('Scripts')),
        Choice(REPORTS, _('Reports')),
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
        Choice(STATUS_PENDING, _('Pending'), color='cyan', description=_('Awaiting execution')),
        Choice(STATUS_SCHEDULED, _('Scheduled'), color='gray', description=_('Scheduled to run at a future time')),
        Choice(STATUS_RUNNING, _('Running'), color='blue', description=_('Currently executing')),
        Choice(STATUS_COMPLETED, _('Completed'), color='green', description=_('Finished successfully')),
        Choice(STATUS_ERRORED, _('Errored'), color='red', description=_('Terminated due to an unhandled error')),
        Choice(STATUS_FAILED, _('Failed'), color='red', description=_('Failed to complete')),
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


class JobNotificationChoices(ChoiceSet):
    NOTIFICATION_ALWAYS = 'always'
    NOTIFICATION_ON_FAILURE = 'on_failure'
    NOTIFICATION_NEVER = 'never'

    CHOICES = (
        Choice(NOTIFICATION_ALWAYS, _('Always'), description=_('Notify after every job execution')),
        Choice(NOTIFICATION_ON_FAILURE, _('On failure'), description=_('Notify only when a job fails')),
        Choice(NOTIFICATION_NEVER, _('Never'), description=_('Never send job notifications')),
    )


class JobIntervalChoices(ChoiceSet):
    INTERVAL_MINUTELY = 1
    INTERVAL_HOURLY = 60
    INTERVAL_DAILY = 60 * 24
    INTERVAL_WEEKLY = 60 * 24 * 7

    CHOICES = (
        Choice(INTERVAL_MINUTELY, _('Minutely')),
        Choice(INTERVAL_HOURLY, _('Hourly')),
        Choice(INTERVAL_HOURLY * 12, _('12 hours')),
        Choice(INTERVAL_DAILY, _('Daily')),
        Choice(INTERVAL_WEEKLY, _('Weekly')),
        Choice(INTERVAL_DAILY * 30, _('30 days')),
    )


#
# ObjectChanges
#

class ObjectChangeActionChoices(ChoiceSet):

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'

    CHOICES = (
        Choice(ACTION_CREATE, _('Created'), color='green'),
        Choice(ACTION_UPDATE, _('Updated'), color='blue'),
        Choice(ACTION_DELETE, _('Deleted'), color='red'),
    )
