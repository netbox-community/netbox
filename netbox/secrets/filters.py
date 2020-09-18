import django_filters
from django.db.models import Q

from dcim.models import Device
from extras.filters import CustomFieldFilterSet, CreatedUpdatedFilterSet
from utilities.filters import BaseFilterSet, NameSlugSearchFilterSet, TagFilter
from .models import Secret, SecretRole


__all__ = (
    'SecretFilterSet',
    'SecretRoleFilterSet',
)


class SecretRoleFilterSet(BaseFilterSet, NameSlugSearchFilterSet):

    class Meta:
        model = SecretRole
        fields = ['id', 'name', 'slug']


class SecretFilterSet(BaseFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SecretRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=SecretRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Secret
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(device__name__icontains=value)
        )
