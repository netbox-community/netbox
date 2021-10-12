import django_filters
from django.db.models import Q

from extras.filters import TagFilter
from netbox.filtersets import PrimaryModelFilterSet
from .models import *

__all__ = (
    'WirelessLANFilterSet',
)


class WirelessLANFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    class Meta:
        model = WirelessLAN
        fields = ['id', 'ssid']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(ssid__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)
