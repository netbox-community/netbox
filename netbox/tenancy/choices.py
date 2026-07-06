from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

#
# Contacts
#


class ContactPriorityChoices(ChoiceSet):
    PRIORITY_PRIMARY = 'primary'
    PRIORITY_SECONDARY = 'secondary'
    PRIORITY_TERTIARY = 'tertiary'
    PRIORITY_INACTIVE = 'inactive'

    CHOICES = (
        Choice(PRIORITY_PRIMARY, _('Primary')),
        Choice(PRIORITY_SECONDARY, _('Secondary')),
        Choice(PRIORITY_TERTIARY, _('Tertiary')),
        Choice(PRIORITY_INACTIVE, _('Inactive')),
    )
