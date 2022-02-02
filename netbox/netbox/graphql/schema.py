import graphene

from circuits.graphql.schema import CircuitsQuery
from dcim.graphql.schema import DCIMQuery
from extras.graphql.schema import ExtrasQuery
from extras.plugins import registry
from ipam.graphql.schema import IPAMQuery
from tenancy.graphql.schema import TenancyQuery
from users.graphql.schema import UsersQuery
from virtualization.graphql.schema import VirtualizationQuery
from wireless.graphql.schema import WirelessQuery

query_types = [
    CircuitsQuery,
    DCIMQuery,
    ExtrasQuery,
    IPAMQuery,
    TenancyQuery,
    UsersQuery,
    VirtualizationQuery,
    WirelessQuery,
    *registry['graphql_queries'],
]

mutation_types = [
    *registry['graphql_mutations'],
]

subscription_types = [
    *registry['graphql_subscriptions'],
]

extra_types = [
    *registry['graphql_types'],
]


class Query(
    *query_types,
    graphene.ObjectType
):
    pass


class Mutation(
    *mutation_types,
    graphene.ObjectType
):
    pass


class Subscription(
    *subscription_types,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query,
                         mutation=Mutation if len(mutation_types) > 0 else None,
                         subscription=Subscription if len(subscription_types) > 0 else None,
                         types=extra_types if len(extra_types) > 0 else None,
                         auto_camelcase=False)
