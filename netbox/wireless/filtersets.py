import django_filters
from django.db.models import Q

from dcim.choices import LinkStatusChoices
from extras.filters import TagFilter
from netbox.filtersets import OrganizationalModelFilterSet, PrimaryModelFilterSet
from .choices import *
from .models import *

__all__ = (
    'WirelessLANFilterSet',
    'WirelessLANGroupFilterSet',
    'WirelessLinkFilterSet',
)


class WirelessLANGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all()
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=WirelessLANGroup.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = WirelessLANGroup
        fields = ['id', 'name', 'slug', 'description']


class WirelessLANFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=WirelessLANGroup.objects.all()
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices
    )
    tag = TagFilter()

    class Meta:
        model = WirelessLAN
        fields = ['id', 'ssid', 'auth_psk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class WirelessLinkFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=LinkStatusChoices
    )
    auth_type = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthTypeChoices
    )
    auth_cipher = django_filters.MultipleChoiceFilter(
        choices=WirelessAuthCipherChoices
    )
    tag = TagFilter()

    class Meta:
        model = WirelessLink
        fields = ['id', 'ssid', 'auth_psk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
