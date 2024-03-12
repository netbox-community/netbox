import strawberry
import strawberry_django
from strawberry import auto
from tenancy import filtersets, models

from netbox.graphql import filter_mixins

__all__ = (
    'TenantFilter',
    'TenantGroupFilter',
    'ContactFilter',
    'ContactRoleFilter',
    'ContactGroupFilter',
    'ContactAssignmentFilter',
)


@strawberry_django.filter(models.Tenant, lookups=True)
class TenantFilter(filtersets.TenantFilterSet):
    id: auto


@strawberry_django.filter(models.TenantGroup, lookups=True)
class TenantGroupFilter(filtersets.TenantGroupFilterSet):
    id: auto


@strawberry_django.filter(models.Contact, lookups=True)
class ContactFilter(filtersets.ContactFilterSet):
    id: auto


@strawberry_django.filter(models.ContactRole, lookups=True)
class ContactRoleFilter(filtersets.ContactRoleFilterSet):
    id: auto


@strawberry_django.filter(models.ContactGroup, lookups=True)
class ContactGroupFilter(filtersets.ContactGroupFilterSet):
    id: auto


@strawberry_django.filter(models.ContactAssignment, lookups=True)
class ContactAssignmentFilter(filtersets.ContactAssignmentFilterSet):
    id: auto
