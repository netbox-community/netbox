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

    CHOICES = [
        (LOCAL, _('Local')),
        (HTTP, _('HTTP(S)')),
        (FTP, _('FTP(S)')),
        (GIT, _('Git')),
    ]
