import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class TenancyQuery(graphene.ObjectType):
    tenant = ObjectField(TenantType)
    tenant_list = ObjectListField(TenantType)

    tenant_group = ObjectField(TenantGroupType)
    tenant_group_list = ObjectListField(TenantGroupType)

    contact = ObjectField(ContactType)
    contact_list = ObjectListField(ContactType)

    contact_role = ObjectField(ContactRoleType)
    contact_role_list = ObjectListField(ContactRoleType)

    contact_group = ObjectField(ContactGroupType)
    contact_group_list = ObjectListField(ContactGroupType)

    contact_assignment = ObjectField(ContactAssignmentType)
    contact_assignment_list = ObjectListField(ContactAssignmentType)
