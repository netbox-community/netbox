from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

__all__ = (
    'TokenVersionChoices',
)


class TokenVersionChoices(ChoiceSet):
    V1 = 1
    V2 = 2

    CHOICES = [
        Choice(V1, _('v1')),
        Choice(V2, _('v2')),
    ]
