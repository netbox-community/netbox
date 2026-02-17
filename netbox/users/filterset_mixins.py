import django_filters
from django.utils.translation import gettext as _

from users.models import Owner, OwnerGroup

__all__ = (
    'OwnerFilterMixin',
)


class OwnerFilterMixin(django_filters.FilterSet):
    """
    Adds owner & owner_id filters for models which inherit from OwnerMixin.
    """
    owner_group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=OwnerGroup.objects.all(),
        distinct=False,
        field_name='owner__group',
        label=_('Owner Group (ID)'),
    )
    owner_group = django_filters.ModelMultipleChoiceFilter(
        queryset=OwnerGroup.objects.all(),
        distinct=False,
        field_name='owner__group__name',
        to_field_name='name',
        label=_('Owner Group (name)'),
    )
    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Owner.objects.all(),
        distinct=False,
        label=_('Owner (ID)'),
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name='owner__name',
        queryset=Owner.objects.all(),
        distinct=False,
        to_field_name='name',
        label=_('Owner (name)'),
    )
