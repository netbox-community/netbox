from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, FilterLookup, StrFilterLookup

from ndx import models
from netbox.graphql.filters import ChangeLoggedModelFilter, register_filter

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from netbox.graphql.filter_lookups import FloatLookup, IntegerLookup

    from .enums import *

__all__ = (
    'EnrichmentFilter',
    'ImportRecordFilter',
)


@register_filter(models.ImportRecord, lookups=True)
class ImportRecordFilter(ChangeLoggedModelFilter):
    object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    object_id: ID | None = strawberry_django.filter_field()
    ndx_id: StrFilterLookup | None = strawberry_django.filter_field()
    entry_type: StrFilterLookup | None = strawberry_django.filter_field()
    vendor_slug: StrFilterLookup | None = strawberry_django.filter_field()
    source: BaseFilterLookup[Annotated['ImportRecordSourceEnum', strawberry.lazy('ndx.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    checksum: StrFilterLookup | None = strawberry_django.filter_field()
    update_available: FilterLookup[bool] | None = strawberry_django.filter_field()


@register_filter(models.Enrichment, lookups=True)
class EnrichmentFilter(ChangeLoggedModelFilter):
    import_record: Annotated['ImportRecordFilter', strawberry.lazy('ndx.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    import_record_id: ID | None = strawberry_django.filter_field()
    tdp_watts: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_operating_temp_c: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    typical_power_draw_watts: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_power_draw_watts: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    ga_date: StrFilterLookup | None = strawberry_django.filter_field()
    eos_date: StrFilterLookup | None = strawberry_django.filter_field()
    last_support_date: StrFilterLookup | None = strawberry_django.filter_field()
    nos: StrFilterLookup | None = strawberry_django.filter_field()
    nos_family: StrFilterLookup | None = strawberry_django.filter_field()
    snmp_sys_object_id: StrFilterLookup | None = strawberry_django.filter_field()
    has_lifecycle: FilterLookup[bool] | None = strawberry_django.filter_field()
    has_thermal: FilterLookup[bool] | None = strawberry_django.filter_field()
    has_environmental: FilterLookup[bool] | None = strawberry_django.filter_field()
    has_operational: FilterLookup[bool] | None = strawberry_django.filter_field()
    has_platform: FilterLookup[bool] | None = strawberry_django.filter_field()
    has_snmp: FilterLookup[bool] | None = strawberry_django.filter_field()
