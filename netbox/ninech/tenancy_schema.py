from graphene import AbstractType
from graphene import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from filter_fields import date_types, string_types, number_types
from tenancy.models import Tenant, TenantGroup

# Nodes
class TenantGroupNode(DjangoObjectType):
    class Meta:
        model = TenantGroup
        interfaces = (Node, )
        filter_fields = {
            'name': string_types,
            'slug': string_types,
        }


class TenantNode(DjangoObjectType):
    class Meta:
        model = Tenant
        interfaces = (Node, )
        filter_fields = {
            'id': ['exact'],
            'name': string_types,
            # 'group__name': string_types,
            'description': string_types,
            'comments': string_types,
        }

# Queries
class TenancyQuery(AbstractType):
    tenant_groups = DjangoFilterConnectionField(TenantGroupNode)
    tenants = DjangoFilterConnectionField(TenantGroupNode)
