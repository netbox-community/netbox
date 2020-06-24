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
        queryset=SecretRole.objects.unrestricted(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=SecretRole.objects.unrestricted(),
        to_field_name='slug',
        label='Role (slug)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.unrestricted(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.unrestricted(),
        to_field_name='name',
        label='Device (name)',
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
