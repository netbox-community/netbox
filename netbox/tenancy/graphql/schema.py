import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class TenancyQuery:
    tenant: TenantType = strawberry_django.field()
    tenant_list: OffsetPaginated[TenantType] = strawberry_django.offset_paginated()

    tenant_group: TenantGroupType = strawberry_django.field()
    tenant_group_list: OffsetPaginated[TenantGroupType] = strawberry_django.offset_paginated()

    contact: ContactType = strawberry_django.field()
    contact_list: OffsetPaginated[ContactType] = strawberry_django.offset_paginated()

    contact_role: ContactRoleType = strawberry_django.field()
    contact_role_list: OffsetPaginated[ContactRoleType] = strawberry_django.offset_paginated()

    contact_group: ContactGroupType = strawberry_django.field()
    contact_group_list: OffsetPaginated[ContactGroupType] = strawberry_django.offset_paginated()

    contact_assignment: ContactAssignmentType = strawberry_django.field()
    contact_assignment_list: OffsetPaginated[ContactAssignmentType] = strawberry_django.offset_paginated()
