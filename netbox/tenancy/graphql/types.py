from typing import Annotated, List

import strawberry
import strawberry_django

from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from tenancy import models
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'ContactAssignmentType',
    'ContactGroupType',
    'ContactRoleType',
    'ContactType',
    'TenantType',
    'TenantGroupType',
)


class ContactAssignmentsMixin:
    # assignments = graphene.List('tenancy.graphql.types.ContactAssignmentType')

    def resolve_assignments(self, info):
        return self.assignments.restrict(info.context.user, 'view')


#
# Tenants
#

@strawberry_django.type(
    models.Tenant,
    fields='__all__',
    filters=TenantFilter
)
class TenantType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.TenantGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=TenantGroupFilter
)
class TenantGroupType(OrganizationalObjectType):
    pass


#
# Contacts
#

@strawberry_django.type(
    models.Contact,
    fields='__all__',
    filters=ContactFilter
)
class ContactType(ContactAssignmentsMixin, NetBoxObjectType):

    @strawberry_django.field
    def assignments(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.assignments.all()


@strawberry_django.type(
    models.ContactRole,
    fields='__all__',
    filters=ContactRoleFilter
)
class ContactRoleType(ContactAssignmentsMixin, OrganizationalObjectType):

    @strawberry_django.field
    def assignments(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.assignments.all()


@strawberry_django.type(
    models.ContactGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=ContactGroupFilter
)
class ContactGroupType(OrganizationalObjectType):

    @strawberry_django.field
    def parent(self) -> Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')]:
        return self.parent

    @strawberry_django.field
    def contacts(self) -> List[ContactType]:
        return self.clusters.all()

    @strawberry_django.field
    def children(self) -> List[Annotated["ContactGroupType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.ContactAssignment,
    fields='__all__',
    filters=ContactAssignmentFilter
)
class ContactAssignmentType(CustomFieldsMixin, TagsMixin, BaseObjectType):
    pass
