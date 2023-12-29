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

    TERMINAL_STATE_CHOICES = (
        STATUS_COMPLETED,
        STATUS_ERRORED,
        STATUS_FAILED,
    )
