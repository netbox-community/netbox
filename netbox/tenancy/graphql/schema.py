from typing import List

import strawberry
import strawberry_django

from tenancy import models
from .types import *


@strawberry.type
class TenancyQuery:
    @strawberry.field
    def tenant(self, id: int) -> TenantType:
        return models.Tenant.objects.get(id=id)
    tenant_list: List[TenantType] = strawberry_django.field()

    @strawberry.field
    def tenant_group(self, id: int) -> TenantGroupType:
        return models.TenantGroup.objects.get(id=id)
    tenant_group_list: List[TenantGroupType] = strawberry_django.field()

    @strawberry.field
    def contact(self, id: int) -> ContactType:
        return models.Contact.objects.get(id=id)
    contact_list: List[ContactType] = strawberry_django.field()

    @strawberry.field
    def contact_role(self, id: int) -> ContactRoleType:
        return models.ContactRole.objects.get(id=id)
    contact_role_list: List[ContactRoleType] = strawberry_django.field()

    @strawberry.field
    def contact_group(self, id: int) -> ContactGroupType:
        return models.ContactGroup.objects.get(id=id)
    contact_group_list: List[ContactGroupType] = strawberry_django.field()

    @strawberry.field
    def contact_assignment(self, id: int) -> ContactAssignmentType:
        return models.ContactAssignment.objects.get(id=id)
    contact_assignment_list: List[ContactAssignmentType] = strawberry_django.field()
