import django_filters
from django.utils.translation import gettext as _

from users.models import Owner

__all__ = (
    'OwnerFilterMixin',
)


class OwnerFilterMixin(django_filters.FilterSet):
    """
    Adds owner & owner_id filters for models which inherit from OwnerMixin.
    """
    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Owner.objects.all(),
        label=_('Owner (ID)'),
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name='owner__name',
        queryset=Owner.objects.all(),
        to_field_name='name',
        label=_('Owner (name)'),
    )
