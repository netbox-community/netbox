import strawberry
from django.conf import settings
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry.extensions import MaxAliasesLimiter
from strawberry.schema.config import StrawberryConfig

from circuits.graphql.schema import CircuitsQuery, CircuitsQueryOld
from core.graphql.schema import CoreQuery, CoreQueryOld
from dcim.graphql.schema import DCIMQuery, DCIMQueryOld
from extras.graphql.schema import ExtrasQuery, ExtrasQueryOld
from ipam.graphql.schema import IPAMQuery, IPAMQueryOld
from netbox.registry import registry
from tenancy.graphql.schema import TenancyQuery, TenancyQueryOld
from users.graphql.schema import UsersQuery, UsersQueryOld
from virtualization.graphql.schema import VirtualizationQuery, VirtualizationQueryOld
from vpn.graphql.schema import VPNQuery, VPNQueryOld
from wireless.graphql.schema import WirelessQuery, WirelessQueryOld

__all__ = (
    'Query',
    'QueryV1',
    'QueryV2',
    'schema_v1',
    'schema_v2',
)


@strawberry.type
class QueryV1(
    UsersQueryOld,
    CircuitsQueryOld,
    CoreQueryOld,
    DCIMQueryOld,
    ExtrasQueryOld,
    IPAMQueryOld,
    TenancyQueryOld,
    VirtualizationQueryOld,
    VPNQueryOld,
    WirelessQueryOld,
    *registry['plugins']['graphql_schemas'],  # Append plugin schemas
):
    """Query class for GraphQL API v1"""
    pass


@strawberry.type
class QueryV2(
    UsersQuery,
    CircuitsQuery,
    CoreQuery,
    DCIMQuery,
    ExtrasQuery,
    IPAMQuery,
    TenancyQuery,
    VirtualizationQuery,
    VPNQuery,
    WirelessQuery,
    *registry['plugins']['graphql_schemas'],  # Append plugin schemas
):
    """Query class for GraphQL API v2"""
    pass


# Expose a default Query class for the configured default GraphQL version
class Query(QueryV2 if settings.GRAPHQL_DEFAULT_VERSION == 2 else QueryV1):
    pass


# Generate schemas for both versions of the GraphQL API
schema_v1 = strawberry.Schema(
    query=QueryV1,
    config=StrawberryConfig(auto_camel_case=False),
    extensions=[
        DjangoOptimizerExtension(prefetch_custom_queryset=True),
        MaxAliasesLimiter(max_alias_count=settings.GRAPHQL_MAX_ALIASES),
    ]
)
schema_v2 = strawberry.Schema(
    query=QueryV2,
    config=StrawberryConfig(auto_camel_case=False),
    extensions=[
        DjangoOptimizerExtension(prefetch_custom_queryset=True),
        MaxAliasesLimiter(max_alias_count=settings.GRAPHQL_MAX_ALIASES),
    ]
)
