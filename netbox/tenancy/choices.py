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
        (PRIORITY_PRIMARY, 'Primary'),
        (PRIORITY_SECONDARY, 'Secondary'),
        (PRIORITY_TERTIARY, 'Tertiary'),
        (PRIORITY_INACTIVE, 'Inactive'),
    )
