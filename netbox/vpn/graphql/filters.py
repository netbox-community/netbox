from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    FilterLookup,
)
from extras.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from core.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import *
# from .filter_mixins import *

from vpn import models

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from core.graphql.filters import *
    from extras.graphql.filters import *
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from tenancy.graphql.filters import *
    from wireless.graphql.filters import *
    from users.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *


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


@strawberry_django.filter(models.TunnelGroup, lookups=True)
class TunnelGroupFilter(OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter(models.TunnelTermination, lookups=True)
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


@strawberry_django.filter(models.Tunnel, lookups=True)
class TunnelFilter(PrimaryModelFilterMixin):
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
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    tunnel_id: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.IKEProposal, lookups=True)
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
    sa_lifetime: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.IKEPolicy, lookups=True)
class IKEPolicyFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    version: Annotated['IKEVersionEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    mode: Annotated['IKEModeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    proposals: Annotated['IKEProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    preshared_key: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.IPSecProposal, lookups=True)
class IPSecProposalFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    encryption_algorithm: Annotated['EncryptionAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    authentication_algorithm: Annotated['AuthenticationAlgorithmEnum', strawberry.lazy('vpn.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime_seconds: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sa_lifetime_data: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.IPSecPolicy, lookups=True)
class IPSecPolicyFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    proposals: Annotated['IPSecProposalFilter', strawberry.lazy('vpn.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    pfs_group: Annotated['DHGroupEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.IPSecProfile, lookups=True)
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


@strawberry_django.filter(models.L2VPN, lookups=True)
class L2VPNFilter(ContactFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated['L2VPNTypeEnum', strawberry.lazy('vpn.graphql.enums')] | None = strawberry_django.filter_field()
    identifier: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    import_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    export_targets: Annotated['RouteTargetFilter', strawberry.lazy('ipam.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.L2VPNTermination, lookups=True)
class L2VPNTerminationFilter(NetBoxModelFilterMixin):
    l2vpn: Annotated['L2VPNFilter', strawberry.lazy('vpn.graphql.filters')] | None = strawberry_django.filter_field()
    l2vpn_id: ID | None = strawberry_django.filter_field()
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
