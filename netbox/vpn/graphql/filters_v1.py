from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1
from extras.graphql.filter_mixins_v1 import CustomFieldsFilterMixinV1, TagsFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    NetBoxModelFilterMixinV1, OrganizationalModelFilterMixinV1, PrimaryModelFilterMixinV1
)
from tenancy.graphql.filter_mixins_v1 import ContactFilterMixinV1, TenancyFilterMixinV1
from vpn import models

if TYPE_CHECKING:
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from ipam.graphql.filters_v1 import IPAddressFilterV1, RouteTargetFilterV1
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'TunnelGroupFilterV1',
    'TunnelTerminationFilterV1',
    'TunnelFilterV1',
    'IKEProposalFilterV1',
    'IKEPolicyFilterV1',
    'IPSecProposalFilterV1',
    'IPSecPolicyFilterV1',
    'IPSecProfileFilterV1',
    'L2VPNFilterV1',
    'L2VPNTerminationFilterV1',
)


@strawberry_django.filter_type(models.TunnelGroup, lookups=True)
class TunnelGroupFilterV1(OrganizationalModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.TunnelTermination, lookups=True)
class TunnelTerminationFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
    tunnel: Annotated['TunnelFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_id: ID | None = strawberry_django.filter_field()
    role: Annotated['TunnelTerminationRoleEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['TunnelTerminationTypeEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type_id: ID | None = strawberry_django.filter_field()
    termination_id: ID | None = strawberry_django.filter_field()
    outside_ip: Annotated['IPAddressFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    outside_ip_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Tunnel, lookups=True)
class TunnelFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['TunnelStatusEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['TunnelGroupFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    encapsulation: Annotated['TunnelEncapsulationEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_profile: Annotated['IPSecProfileFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['TunnelTerminationFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEProposal, lookups=True)
class IKEProposalFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    authentication_method: Annotated['AuthenticationMethodEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    encryption_algorithm: Annotated['EncryptionAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    authentication_algorithm: Annotated['AuthenticationAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    sa_lifetime: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    ike_policies: Annotated['IKEPolicyFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEPolicy, lookups=True)
class IKEPolicyFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    version: Annotated['IKEVersionEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    mode: Annotated['IKEModeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    proposals: Annotated['IKEProposalFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    preshared_key: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.IPSecProposal, lookups=True)
class IPSecProposalFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    encryption_algorithm: Annotated['EncryptionAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    authentication_algorithm: Annotated['AuthenticationAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime_seconds: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime_data: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_policies: Annotated['IPSecPolicyFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IPSecPolicy, lookups=True)
class IPSecPolicyFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    proposals: Annotated['IPSecProposalFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    pfs_group: Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.IPSecProfile, lookups=True)
class IPSecProfileFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    mode: Annotated['IPSecModeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    ike_policy: Annotated['IKEPolicyFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    ike_policy_id: ID | None = strawberry_django.filter_field()
    ipsec_policy: Annotated['IPSecPolicyFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_policy_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.L2VPN, lookups=True)
class L2VPNFilterV1(ContactFilterMixinV1, TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated['L2VPNTypeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    identifier: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    import_targets: Annotated['RouteTargetFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['L2VPNTerminationFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.L2VPNTermination, lookups=True)
class L2VPNTerminationFilterV1(NetBoxModelFilterMixinV1):
    l2vpn: Annotated['L2VPNFilterV1', strawberry.lazy('vpn.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    l2vpn_id: ID | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
