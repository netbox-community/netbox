from graphene import AbstractType
from graphene import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from circuits.models import CircuitType, Circuit, Provider
from filter_fields import date_types, string_types, number_types


# Nodes
class ProviderNode(DjangoObjectType):
    class Meta:
        model = Provider
        interfaces = (Node, )
        filter_fields = {
            'name': string_types,
            'slug': ['exact'],
        }
        # filter_order_by = ('id')

class CircuitNode(DjangoObjectType):
    class Meta:
        model = Circuit
        interfaces = (Node, )
        filter_fields = {
            'id': ['exact'],
            'cid': string_types,
            'commit_rate': number_types,
            'install_date': date_types,
            'description': string_types,
            'comments': string_types,
        }
        # filter_order_by = ('id', 'cid')

class TypeNode(DjangoObjectType):
    class Meta:
        model = CircuitType
        interfaces = (Node, )
        filter_fields = {
            'name': string_types,
            'slug': string_types,
        }
        # filter_order_by = ('slug')

# Queries
class CircuitsQuery(AbstractType):
    providers = DjangoFilterConnectionField(ProviderNode)
    types = DjangoFilterConnectionField(TypeNode)
    circuit = Node.Field(CircuitNode)
    circuits = DjangoFilterConnectionField(CircuitNode)
