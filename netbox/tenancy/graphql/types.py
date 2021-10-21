import graphene

from tenancy import filtersets, models
from netbox.graphql.types import OrganizationalObjectType, PrimaryObjectType

__all__ = (
    'ContactAssignmentType',
    'ContactGroupType',
    'ContactRoleType',
    'ContactType',
    'TenantType',
    'TenantGroupType',
)


class ContactAssignmentsMixin:
    assignments = graphene.List('tenancy.graphql.types.ContactAssignmentType')

    def resolve_assignments(self, info):
        return self.assignments.restrict(info.context.user, 'view')


#
# Tenants
#

class TenantType(PrimaryObjectType):

    class Meta:
        model = models.Tenant
        fields = '__all__'
        filterset_class = filtersets.TenantFilterSet


class TenantGroupType(OrganizationalObjectType):

    class Meta:
        model = models.TenantGroup
        fields = '__all__'
        filterset_class = filtersets.TenantGroupFilterSet


#
# Contacts
#

class ContactType(ContactAssignmentsMixin, PrimaryObjectType):

    class Meta:
        model = models.Contact
        fields = '__all__'
        filterset_class = filtersets.ContactFilterSet


class ContactRoleType(ContactAssignmentsMixin, OrganizationalObjectType):

    class Meta:
        model = models.ContactRole
        fields = '__all__'
        filterset_class = filtersets.ContactRoleFilterSet


class ContactGroupType(OrganizationalObjectType):

    class Meta:
        model = models.ContactGroup
        fields = '__all__'
        filterset_class = filtersets.ContactGroupFilterSet


class ContactAssignmentType(OrganizationalObjectType):

    class Meta:
        model = models.ContactAssignment
        fields = '__all__'
        filterset_class = filtersets.ContactAssignmentFilterSet
