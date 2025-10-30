import strawberry
from django.conf import settings
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry.extensions import MaxAliasesLimiter
from strawberry.schema.config import StrawberryConfig

from circuits.graphql.schema_v1 import CircuitsQueryV1
from circuits.graphql.schema import CircuitsQuery
from core.graphql.schema_v1 import CoreQueryV1
from core.graphql.schema import CoreQuery
from dcim.graphql.schema_v1 import DCIMQueryV1
from dcim.graphql.schema import DCIMQuery
from extras.graphql.schema_v1 import ExtrasQueryV1
from extras.graphql.schema import ExtrasQuery
from ipam.graphql.schema_v1 import IPAMQueryV1
from ipam.graphql.schema import IPAMQuery
from netbox.registry import registry
from tenancy.graphql.schema_v1 import TenancyQueryV1
from tenancy.graphql.schema import TenancyQuery
from users.graphql.schema_v1 import UsersQueryV1
from users.graphql.schema import UsersQuery
from virtualization.graphql.schema_v1 import VirtualizationQueryV1
from virtualization.graphql.schema import VirtualizationQuery
from vpn.graphql.schema_v1 import VPNQueryV1
from vpn.graphql.schema import VPNQuery
from wireless.graphql.schema_v1 import WirelessQueryV1
from wireless.graphql.schema import WirelessQuery

__all__ = (
    'Query',
    'QueryV1',
    'QueryV2',
    'schema_v1',
    'schema_v2',
)


@strawberry.type
class QueryV1(
    UsersQueryV1,
    CircuitsQueryV1,
    CoreQueryV1,
    DCIMQueryV1,
    ExtrasQueryV1,
    IPAMQueryV1,
    TenancyQueryV1,
    VirtualizationQueryV1,
    VPNQueryV1,
    WirelessQueryV1,
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
