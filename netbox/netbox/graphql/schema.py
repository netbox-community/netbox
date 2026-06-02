import strawberry
from django.conf import settings
from strawberry.extensions import MaxAliasesLimiter, QueryDepthLimiter, SchemaExtension
from strawberry.schema.config import StrawberryConfig
from strawberry_django.optimizer import DjangoOptimizerExtension

from circuits.graphql.schema import CircuitsQuery
from core.graphql.schema import CoreQuery
from dcim.graphql.schema import DCIMQuery
from extras.graphql.schema import ExtrasQuery
from ipam.graphql.schema import IPAMQuery
from netbox.registry import registry
from tenancy.graphql.schema import TenancyQuery
from users.graphql.schema import UsersQuery
from virtualization.graphql.schema import VirtualizationQuery
from vpn.graphql.schema import VPNQuery
from wireless.graphql.schema import WirelessQuery

from .scalars import BigInt, BigIntScalar


@strawberry.type
class Query(
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
    pass


def get_schema_extensions() -> list[SchemaExtension]:
    extensions: list[SchemaExtension] = [
        DjangoOptimizerExtension(prefetch_custom_queryset=True),
        MaxAliasesLimiter(max_alias_count=settings.GRAPHQL_MAX_ALIASES),
    ]
    max_depth = settings.GRAPHQL_MAX_QUERY_DEPTH
    if max_depth and max_depth > 0:
        extensions.append(QueryDepthLimiter(max_depth=max_depth))
    return extensions


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(
        auto_camel_case=False,
        scalar_map={
            BigInt: BigIntScalar,
        },
    ),
    extensions=get_schema_extensions(),
)
