import django_filters
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import ChangeLoggedModelFilterSet
from utilities.filters import MultiValueContentTypeFilter
from utilities.filtersets import register_filterset

from .choices import *
from .models import *

__all__ = (
    'EnrichmentFilterSet',
    'ImportRecordFilterSet',
)


@register_filterset
class ImportRecordFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type = MultiValueContentTypeFilter()
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContentType.objects.all(),
        distinct=False,
        label=_('Object type (ID)'),
    )
    source = django_filters.MultipleChoiceFilter(
        choices=ImportRecordSourceChoices,
        distinct=False,
    )
    has_enrichment = django_filters.BooleanFilter(
        field_name='enrichment',
        lookup_expr='isnull',
        exclude=True,
        label=_('Has enrichment'),
    )

    class Meta:
        model = ImportRecord
        fields = (
            'id', 'object_id', 'ndx_id', 'entry_type', 'vendor_slug', 'checksum', 'update_available',
            'last_imported',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(ndx_id__icontains=value) |
            Q(vendor_slug__icontains=value)
        )


@register_filterset
class EnrichmentFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    import_record_id = django_filters.ModelMultipleChoiceFilter(
        field_name='import_record',
        queryset=ImportRecord.objects.all(),
        distinct=False,
        label=_('Import record (ID)'),
    )

    class Meta:
        model = Enrichment
        fields = (
            'id', 'tdp_watts', 'airflow_cfm', 'cooling_type', 'ga_date', 'eol_announced', 'eos_date', 'eosw_date',
            'eosec_date', 'last_support_date', 'max_operating_temp_c', 'min_operating_temp_c',
            'max_operating_humidity', 'min_operating_humidity', 'max_operating_altitude_m', 'ingress_protection',
            'mtbf_hours', 'typical_power_draw_watts', 'max_power_draw_watts', 'noise_level_dba',
            'power_capacity_watts', 'nos', 'nos_family', 'snmp_sys_object_id', 'snmp_vendor_oid_prefix',
            'has_lifecycle', 'has_thermal', 'has_environmental', 'has_operational', 'has_platform', 'has_snmp',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(import_record__ndx_id__icontains=value) |
            Q(nos__icontains=value) |
            Q(nos_family__icontains=value)
        )
