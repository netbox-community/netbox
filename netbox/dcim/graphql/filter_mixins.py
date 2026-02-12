from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import BaseFilterLookup, FilterLookup

from core.graphql.filters import ContentTypeFilter

from .enums import *

if TYPE_CHECKING:
    from dcim.graphql.filters import LocationFilter, RegionFilter, SiteFilter, SiteGroupFilter
    from extras.graphql.filters import ConfigTemplateFilter
    from ipam.graphql.filters import VLANFilter, VLANTranslationPolicyFilter
    from netbox.graphql.filter_lookups import IntegerLookup

    from .filters import *

__all__ = (
    'CabledObjectModelFilterMixin',
    'ComponentModelFilterMixin',
    'ComponentTemplateFilterMixin',
    'InterfaceBaseFilterMixin',
    'ModularComponentFilterMixin',
    'ModularComponentTemplateFilterMixin',
    'RackFilterMixin',
    'RenderConfigFilterMixin',
    'ScopedFilterMixin',
)


@dataclass
class ScopedFilterMixin:
    scope_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    scope_id: ID | None = strawberry_django.filter_field()

    # Cached relations
    _location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='location')
    )
    _region: Annotated['RegionFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='region')
    )
    _site_group: Annotated['SiteGroupFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='site_group')
    )
    _site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='site')
    )


@dataclass
class ComponentModelFilterMixin:
    _site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='site')
    )
    _location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='location')
    )
    _rack: Annotated['RackFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='rack')
    )
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ModularComponentFilterMixin(ComponentModelFilterMixin):
    module: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    module_id: ID | None = strawberry_django.filter_field()
    inventory_items: Annotated['InventoryItemFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class CabledObjectModelFilterMixin:
    cable: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: (
        BaseFilterLookup[Annotated['CableEndEnum', strawberry.lazy('dcim.graphql.enums')]] | None
    ) = strawberry_django.filter_field()
    mark_connected: FilterLookup[bool] | None = strawberry_django.filter_field()


@dataclass
class ComponentTemplateFilterMixin:
    device_type: Annotated['DeviceTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    device_type_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ModularComponentTemplateFilterMixin(ComponentTemplateFilterMixin):
    module_type: Annotated['ModuleTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class RenderConfigFilterMixin:
    config_template: Annotated['ConfigTemplateFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@dataclass
class InterfaceBaseFilterMixin:
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mtu: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    mode: (
        BaseFilterLookup[Annotated['InterfaceModeEnum', strawberry.lazy('dcim.graphql.enums')]] | None
    ) = strawberry_django.filter_field()
    bridge: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    bridge_id: ID | None = strawberry_django.filter_field()
    untagged_vlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tagged_vlans: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    qinq_svlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    vlan_translation_policy: (
            Annotated['VLANTranslationPolicyFilter', strawberry.lazy('ipam.graphql.filters')] | None
    ) = strawberry_django.filter_field()
    primary_mac_address: Annotated['MACAddressFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_mac_address_id: ID | None = strawberry_django.filter_field()


@dataclass
class RackFilterMixin:
    width: BaseFilterLookup[Annotated['RackWidthEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    u_height: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    starting_unit: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    desc_units: FilterLookup[bool] | None = strawberry_django.filter_field()
    outer_width: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    outer_height: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    outer_depth: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    outer_unit: BaseFilterLookup[Annotated['RackDimensionUnitEnum', strawberry.lazy('dcim.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    mounting_depth: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
