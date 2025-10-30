from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1, ChangeLogFilterMixinV1
from core.graphql.filters_v1 import ContentTypeFilterV1
from netbox.graphql.filter_mixins_v1 import NetBoxModelFilterMixinV1, PrimaryModelFilterMixinV1, WeightFilterMixinV1
from .enums import *

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup
    from extras.graphql.filters_v1 import ConfigTemplateFilterV1
    from ipam.graphql.filters_v1 import VLANFilterV1, VLANTranslationPolicyFilterV1
    from .filters_v1 import *

__all__ = (
    'CabledObjectModelFilterMixinV1',
    'ComponentModelFilterMixinV1',
    'ComponentTemplateFilterMixinV1',
    'InterfaceBaseFilterMixinV1',
    'ModularComponentModelFilterMixinV1',
    'ModularComponentTemplateFilterMixinV1',
    'RackBaseFilterMixinV1',
    'RenderConfigFilterMixinV1',
    'ScopedFilterMixinV1',
)


@dataclass
class ScopedFilterMixinV1(BaseFilterMixinV1):
    scope_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    scope_id: ID | None = strawberry_django.filter_field()


@dataclass
class ComponentModelFilterMixinV1(NetBoxModelFilterMixinV1):
    device: Annotated['DeviceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ModularComponentModelFilterMixinV1(ComponentModelFilterMixinV1):
    module: Annotated['ModuleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    module_id: ID | None = strawberry_django.filter_field()
    inventory_items: Annotated['InventoryItemFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class CabledObjectModelFilterMixinV1(BaseFilterMixinV1):
    cable: Annotated['CableFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: CableEndEnum | None = strawberry_django.filter_field()
    mark_connected: FilterLookup[bool] | None = strawberry_django.filter_field()


@dataclass
class ComponentTemplateFilterMixinV1(ChangeLogFilterMixinV1):
    device_type: Annotated['DeviceTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_type_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ModularComponentTemplateFilterMixinV1(ComponentTemplateFilterMixinV1):
    module_type: Annotated['ModuleTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class RenderConfigFilterMixinV1(BaseFilterMixinV1):
    config_template: Annotated['ConfigTemplateFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@dataclass
class InterfaceBaseFilterMixinV1(BaseFilterMixinV1):
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mtu: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    mode: InterfaceModeEnum | None = strawberry_django.filter_field()
    bridge: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    bridge_id: ID | None = strawberry_django.filter_field()
    untagged_vlan: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tagged_vlans: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    qinq_svlan: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_translation_policy: Annotated[
        'VLANTranslationPolicyFilterV1', strawberry.lazy('ipam.graphql.filters_v1')
    ] | None = strawberry_django.filter_field()
    primary_mac_address: Annotated['MACAddressFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    primary_mac_address_id: ID | None = strawberry_django.filter_field()


@dataclass
class RackBaseFilterMixinV1(WeightFilterMixinV1, PrimaryModelFilterMixinV1):
    width: Annotated['RackWidthEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
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
    outer_unit: Annotated['RackDimensionUnitEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    mounting_depth: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
