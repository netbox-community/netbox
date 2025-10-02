from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet

__all__ = (
    'TokenVersionChoices',
)


class TokenVersionChoices(ChoiceSet):
    V1 = 1
    V2 = 2

    CHOICES = [
        (V1, _('v1')),
        (V2, _('v2')),
    ]
