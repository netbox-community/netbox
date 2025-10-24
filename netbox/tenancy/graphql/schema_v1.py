from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class TenancyQueryV1:
    tenant: TenantTypeV1 = strawberry_django.field()
    tenant_list: List[TenantTypeV1] = strawberry_django.field()

    tenant_group: TenantGroupTypeV1 = strawberry_django.field()
    tenant_group_list: List[TenantGroupTypeV1] = strawberry_django.field()

    contact: ContactTypeV1 = strawberry_django.field()
    contact_list: List[ContactTypeV1] = strawberry_django.field()

    contact_role: ContactRoleTypeV1 = strawberry_django.field()
    contact_role_list: List[ContactRoleTypeV1] = strawberry_django.field()

    contact_group: ContactGroupTypeV1 = strawberry_django.field()
    contact_group_list: List[ContactGroupTypeV1] = strawberry_django.field()

    contact_assignment: ContactAssignmentTypeV1 = strawberry_django.field()
    contact_assignment_list: List[ContactAssignmentTypeV1] = strawberry_django.field()
