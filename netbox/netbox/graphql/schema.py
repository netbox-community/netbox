import graphene

from circuits.graphql.schema import CircuitsQuery
from dcim.graphql.schema import DCIMQuery
from extras.graphql.schema import ExtrasQuery
from extras.registry import registry
from ipam.graphql.schema import IPAMQuery
from tenancy.graphql.schema import TenancyQuery
from users.graphql.schema import UsersQuery
from virtualization.graphql.schema import VirtualizationQuery
from wireless.graphql.schema import WirelessQuery


class Query(
    CircuitsQuery,
    DCIMQuery,
    ExtrasQuery,
    IPAMQuery,
    TenancyQuery,
    UsersQuery,
    VirtualizationQuery,
    WirelessQuery,
    *registry['plugins']['graphql_schemas'],  # Append plugin schemas
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, auto_camelcase=False)
