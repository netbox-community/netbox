import django_filters
from django.db.models import Q

from ipam.models import IPAddress
from .models import (
    Zone,
    Record,
)
from .forms import record_type_choices


class ZoneFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        name='name',
        lookup_type='icontains',
        label='Name',
    )

    class Meta:
        model = Zone
        fields = ['name']


class RecordFilter(django_filters.FilterSet):
    zone__name = django_filters.ModelMultipleChoiceFilter(
        name='zone__name',
        to_field_name='name',
        lookup_type='icontains',
        queryset=Zone.objects.all(),
        label='Zone (Name)',
    )
    record_type = django_filters.MultipleChoiceFilter(
        name='record_type',
        label='Type',
        choices=record_type_choices
    )
    name = django_filters.CharFilter(
        name='name',
        lookup_type='icontains',
        label='Name',
    )
    name_or_value_or_ip = django_filters.MethodFilter(
        name='name_or_value_or_ip',
    )

    class Meta:
        model = Record
        field = ['name', 'record_type', 'value']

    def filter_name_or_value_or_ip(self, queryset, value):
        if not value:
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(value__icontains=value) | Q(address__address__icontains=value))
