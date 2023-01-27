from django.utils.translation import gettext as _

from utilities.choices import ChoiceSet


#
# Data sources
#

class DataSourceTypeChoices(ChoiceSet):
    LOCAL = 'local'
    HTTP = 'http'
    FTP = 'ftp'
    GIT = 'git'

    CHOICES = (
        (LOCAL, _('Local')),
        (HTTP, _('HTTP(S)')),
        (FTP, _('FTP(S)')),
        (GIT, _('Git')),
    )


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
