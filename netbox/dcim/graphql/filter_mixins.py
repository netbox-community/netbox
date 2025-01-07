from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry import ID
import strawberry_django
from strawberry_django import FilterLookup
from core.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from .enums import *

if TYPE_CHECKING:
    from .filters import *
    from core.graphql.filter_lookups import *
    from extras.graphql.filters import *
    from ipam.graphql.filters import *

__all__ = [
    'ComponentModelFilterMixin',
    'ModularComponentModelFilterMixin',
    'CabledObjectModelFilterMixin',
    'ComponentTemplateFilterMixin',
    'ModularComponentTemplateFilterMixin',
    'RenderConfigFilterMixin',
    'InterfaceBaseFilterMixin',
    'RackBaseFilterMixin',
]


@dataclass
class ComponentModelFilterMixin(NetBoxModelFilterMixin):
    device: Annotated['DeviceFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    lable: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ModularComponentModelFilterMixin(ComponentModelFilterMixin):
    module: Annotated['ModuleFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    module_id: ID | None = strawberry_django.filter_field()
    inventory_items: Annotated['InventoryItemFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class CabledObjectModelFilterMixin(BaseFilterMixin):
    cable: Annotated['CableFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    cable_id: ID | None = strawberry_django.filter_field()
    cable_end: CableEndEnum | None = strawberry_django.filter_field()
    mark_connected: FilterLookup[bool] | None = strawberry_django.filter_field()


@dataclass
class ComponentTemplateFilterMixin(ChangeLogFilterMixin):
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
class RenderConfigFilterMixin(BaseFilterMixin):
    config_template: Annotated['ConfigTemplateFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    config_template_id: ID | None = strawberry_django.filter_field()


@dataclass
class InterfaceBaseFilterMixin(BaseFilterMixin):
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    mtu: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    mode: InterfaceModeEnum | None = strawberry_django.filter_field()
    parent: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()
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
    vlan_tranlation_policy: Annotated['VLANTranslationPolicyFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_mac_address: Annotated['MACAddressFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    primary_mac_address_id: ID | None = strawberry_django.filter_field()


@dataclass
class RackBaseFilterMixin(WeightFilterMixin, PrimaryModelFilterMixin):
    width: Annotated['RackWidthEnum', strawberry.lazy('dcim.graphql.enums')] | None = strawberry_django.filter_field()
    u_height: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    starting_unit: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    desc_units: FilterLookup[bool] | None = strawberry_django.filter_field()
    outer_width: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    outer_depth: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    outer_unit: Annotated['RackDimensionUnitEnum', strawberry.lazy('dcim.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    mounting_depth: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    max_weight: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
