from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


#
# Contacts
#

class ContactPriorityChoices(ChoiceSet):
    PRIORITY_PRIMARY = 'primary'
    PRIORITY_SECONDARY = 'secondary'
    PRIORITY_TERTIARY = 'tertiary'
    PRIORITY_INACTIVE = 'inactive'

    CHOICES = (
        (PRIORITY_PRIMARY, _('Primary')),
        (PRIORITY_SECONDARY, _('Secondary')),
        (PRIORITY_TERTIARY, _('Tertiary')),
        (PRIORITY_INACTIVE, _('Inactive')),
    )
