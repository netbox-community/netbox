import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from tenancy import models
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer


class TenancyQuery(graphene.ObjectType):
    tenant = ObjectField(TenantType)
    tenant_list = ObjectListField(TenantType)

    def resolve_tenant_list(root, info, **kwargs):
        return gql_query_optimizer(models.Tenant.objects.all(), info)

    tenant_group = ObjectField(TenantGroupType)
    tenant_group_list = ObjectListField(TenantGroupType)

    def resolve_tenant_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.TenantGroup.objects.all(), info)

    contact = ObjectField(ContactType)
    contact_list = ObjectListField(ContactType)

    def resolve_contact_list(root, info, **kwargs):
        return gql_query_optimizer(models.Contact.objects.all(), info)

    contact_role = ObjectField(ContactRoleType)
    contact_role_list = ObjectListField(ContactRoleType)

    def resolve_contact_role_list(root, info, **kwargs):
        return gql_query_optimizer(models.ContactRole.objects.all(), info)

    contact_group = ObjectField(ContactGroupType)
    contact_group_list = ObjectListField(ContactGroupType)

    def resolve_contact_group_list(root, info, **kwargs):
        return gql_query_optimizer(models.ContactGroup.objects.all(), info)

    contact_assignment = ObjectField(ContactAssignmentType)
    contact_assignment_list = ObjectListField(ContactAssignmentType)

    def resolve_contact_assignment_list(root, info, **kwargs):
        return gql_query_optimizer(models.ContactAssignment.objects.all(), info)
