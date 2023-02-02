from django.utils.translation import gettext as _

from utilities.choices import ChoiceSet


#
# Data sources
#

class DataSourceTypeChoices(ChoiceSet):
    LOCAL = 'local'
    GIT = 'git'

    CHOICES = (
        (LOCAL, _('Local'), 'gray'),
        (GIT, _('Git'), 'blue'),
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
