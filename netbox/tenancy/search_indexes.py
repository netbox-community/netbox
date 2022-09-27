import tenancy.filtersets
import tenancy.tables
from django.db import models
from search.models import SearchMixin
from tenancy.models import Contact, ContactAssignment, Tenant
from utilities.utils import count_related


class TenantIndex(SearchMixin):
    model = Tenant
    queryset = Tenant.objects.prefetch_related('group')
    filterset = tenancy.filtersets.TenantFilterSet
    table = tenancy.tables.TenantTable
    url = 'tenancy:tenant_list'
    choice_header = 'Tenancy'


class ContactIndex(SearchMixin):
    model = Contact
    queryset = Contact.objects.prefetch_related('group', 'assignments').annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = tenancy.filtersets.ContactFilterSet
    table = tenancy.tables.ContactTable
    url = 'tenancy:contact_list'
    choice_header = 'Tenancy'


TENANCY_SEARCH_TYPES = {
    'tenant': TenantIndex,
    'contact': ContactIndex,
}
