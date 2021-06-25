import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class TenancyQuery(graphene.ObjectType):
    tenant = ObjectField(TenantType)
    tenants = ObjectListField(TenantType)

    tenant_group = ObjectField(TenantGroupType)
    tenant_groups = ObjectListField(TenantGroupType)
