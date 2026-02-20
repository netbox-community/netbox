from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, FilterLookup

from extras.graphql.filter_mixins import CustomFieldsFilterMixin, TagsFilterMixin
from netbox.graphql.filters import (
    ChangeLoggedModelFilter,
    NetBoxModelFilter,
    OrganizationalModelFilter,
    PrimaryModelFilter,
)
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from vpn import models

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from ipam.graphql.filters import IPAddressFilter, RouteTargetFilter
    from netbox.graphql.filter_lookups import BigIntegerLookup, IntegerLookup

    from .enums import *

__all__ = (
    'IKEPolicyFilter',
    'IKEProposalFilter',
    'IPSecPolicyFilter',
    'IPSecProfileFilter',
    'IPSecProposalFilter',
    'L2VPNFilter',
    'L2VPNTerminationFilter',
    'TunnelFilter',
    'TunnelGroupFilter',
    'TunnelTerminationFilter',
)


@strawberry_django.filter_type(models.TunnelGroup, lookups=True)
class TunnelGroupFilter(OrganizationalModelFilter):
    pass


@strawberry_django.filter_type(models.TunnelTermination, lookups=True)
class TunnelTerminationFilter(CustomFieldsFilterMixin, TagsFilterMixin, ChangeLoggedModelFilter):
    tunnel: Annotated['TunnelFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    tunnel_id: ID | None = strawberry_django.filter_field()
    role: BaseFilterLookup[Annotated['TunnelTerminationRoleEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    termination_type: (
        BaseFilterLookup[Annotated['TunnelTerminationTypeEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    termination_type_id: ID | None = strawberry_django.filter_field()
    termination_id: ID | None = strawberry_django.filter_field()
    outside_ip: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    outside_ip_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Tunnel, lookups=True)
class TunnelFilter(TenancyFilterMixin, PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: BaseFilterLookup[Annotated['TunnelStatusEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['TunnelGroupFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    encapsulation: (
        BaseFilterLookup[Annotated['TunnelEncapsulationEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    ipsec_profile: Annotated['IPSecProfileFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_id: Annotated['BigIntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['TunnelTerminationFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEProposal, lookups=True)
class IKEProposalFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    authentication_method: (
        BaseFilterLookup[Annotated['AuthenticationMethodEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    encryption_algorithm: (
        BaseFilterLookup[Annotated['EncryptionAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    authentication_algorithm: (
        BaseFilterLookup[Annotated['AuthenticationAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    group: BaseFilterLookup[Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    ike_policies: Annotated['IKEPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEPolicy, lookups=True)
class IKEPolicyFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    version: BaseFilterLookup[Annotated['IKEVersionEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    mode: BaseFilterLookup[Annotated['IKEModeEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    proposals: Annotated['IKEProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    preshared_key: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.IPSecProposal, lookups=True)
class IPSecProposalFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    encryption_algorithm: (
        BaseFilterLookup[Annotated['EncryptionAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')]] | None
    ) = (
        strawberry_django.filter_field()
    )
    authentication_algorithm: (
        BaseFilterLookup[
            BaseFilterLookup[Annotated['AuthenticationAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')]]
        ] | None
    ) = (
        strawberry_django.filter_field()
    )
    sa_lifetime_seconds: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime_data: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_policies: Annotated['IPSecPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IPSecPolicy, lookups=True)
class IPSecPolicyFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    proposals: Annotated['IPSecProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    pfs_group: BaseFilterLookup[Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IPSecProfile, lookups=True)
class IPSecProfileFilter(PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    mode: BaseFilterLookup[Annotated['IPSecModeEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    ike_policy: Annotated['IKEPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ike_policy_id: ID | None = strawberry_django.filter_field()
    ipsec_policy: Annotated['IPSecPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_policy_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.L2VPN, lookups=True)
class L2VPNFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    type: BaseFilterLookup[Annotated['L2VPNTypeEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
    identifier: Annotated['BigIntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    import_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['L2VPNTerminationFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    status: BaseFilterLookup[Annotated['L2VPNStatusEnum', strawberry.lazy('vpn.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.L2VPNTermination, lookups=True)
class L2VPNTerminationFilter(NetBoxModelFilter):
    l2vpn: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    l2vpn_id: ID | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
