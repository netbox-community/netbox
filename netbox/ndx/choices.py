from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet


class ImportRecordSourceChoices(ChoiceSet):
    SOURCE_COMMUNITY = 'community'
    SOURCE_NETBOX_LABS = 'netbox_labs'
    SOURCE_BOTH = 'both'

    CHOICES = [
        Choice(SOURCE_COMMUNITY, _('Community'), color='gray'),
        Choice(SOURCE_NETBOX_LABS, _('NetBox Labs'), color='green'),
        Choice(SOURCE_BOTH, _('NetBox Labs & Community'), color='green'),
    ]
