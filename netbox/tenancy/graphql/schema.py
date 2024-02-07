from typing import List
import strawberry
import strawberry_django

from circuits import models
from .types import *


@strawberry.type
class TenancyQuery:
    tenant: TenantType = strawberry_django.field()
    tenant_list: List[TenantType] = strawberry_django.field()

    tenant_group: TenantGroupType = strawberry_django.field()
    tenant_group_list: List[TenantGroupType] = strawberry_django.field()

    contact: ContactType = strawberry_django.field()
    contact_list: List[ContactType] = strawberry_django.field()

    contact_role: ContactRoleType = strawberry_django.field()
    contact_role_list: List[ContactRoleType] = strawberry_django.field()

    contact_group: ContactGroupType = strawberry_django.field()
    contact_group_list: List[ContactGroupType] = strawberry_django.field()

    contact_assignment: ContactAssignmentType = strawberry_django.field()
    contact_assignment_list: List[ContactAssignmentType] = strawberry_django.field()
