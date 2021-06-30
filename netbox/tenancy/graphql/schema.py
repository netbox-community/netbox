import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class TenancyQuery(graphene.ObjectType):
    tenant = ObjectField(TenantType)
    tenant_list = ObjectListField(TenantType)

    tenant_group = ObjectField(TenantGroupType)
    tenant_group_list = ObjectListField(TenantGroupType)
