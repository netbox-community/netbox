from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins import BaseObjectTypeFilterMixin, ChangeLogFilterMixin
from extras.graphql.filter_mixins import CustomFieldsFilterMixin, TagsFilterMixin
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin, OrganizationalModelFilterMixin, PrimaryModelFilterMixin
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from vpn import models

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from ipam.graphql.filters import IPAddressFilter, RouteTargetFilter
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'TunnelGroupFilter',
    'TunnelTerminationFilter',
    'TunnelFilter',
    'IKEProposalFilter',
    'IKEPolicyFilter',
    'IPSecProposalFilter',
    'IPSecPolicyFilter',
    'IPSecProfileFilter',
    'L2VPNFilter',
    'L2VPNTerminationFilter',
)


@strawberry_django.filter_type(models.TunnelGroup, lookups=True)
class TunnelGroupFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter_type(models.TunnelTermination, lookups=True)
class TunnelTerminationFilter(
    BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin
):
    tunnel: Annotated['TunnelFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    tunnel_id: ID | None = strawberry_django.filter_field()
    role: Annotated['TunnelTerminationRoleEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['TunnelTerminationTypeEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type_id: ID | None = strawberry_django.filter_field()
    termination_id: ID | None = strawberry_django.filter_field()
    outside_ip: Annotated['IPAddressFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    outside_ip_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Tunnel, lookups=True)
class TunnelFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['TunnelStatusEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['TunnelGroupFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    encapsulation: Annotated['TunnelEncapsulationEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_profile: Annotated['IPSecProfileFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tunnel_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['TunnelTerminationFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEProposal, lookups=True)
class IKEProposalFilter(PrimaryModelFilterMixin):
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
    ike_policies: Annotated['IKEPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IKEPolicy, lookups=True)
class IKEPolicyFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    version: Annotated['IKEVersionEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    mode: Annotated['IKEModeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    proposals: Annotated['IKEProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    preshared_key: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.IPSecProposal, lookups=True)
class IPSecProposalFilter(PrimaryModelFilterMixin):
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
    ipsec_policies: Annotated['IPSecPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.IPSecPolicy, lookups=True)
class IPSecPolicyFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    proposals: Annotated['IPSecProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    pfs_group: Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.IPSecProfile, lookups=True)
class IPSecProfileFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    mode: Annotated['IPSecModeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    ike_policy: Annotated['IKEPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ike_policy_id: ID | None = strawberry_django.filter_field()
    ipsec_policy: Annotated['IPSecPolicyFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    ipsec_policy_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.L2VPN, lookups=True)
class L2VPNFilter(ContactFilterMixin, TenancyFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated['L2VPNTypeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    identifier: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
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


@strawberry_django.filter_type(models.L2VPNTermination, lookups=True)
class L2VPNTerminationFilter(NetBoxModelFilterMixin):
    l2vpn: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    l2vpn_id: ID | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
