import tenancy.filtersets
import tenancy.tables
from django.db import models
from search.models import SearchMixin
from tenancy.models import Contact, ContactAssignment, Tenant
from utilities.utils import count_related


class TenantIndex(SearchMixin):
    def __init__(self):
        self.model = Tenant
        self.queryset = Tenant.objects.prefetch_related('group')
        self.filterset = tenancy.filtersets.TenantFilterSet
        self.table = tenancy.tables.TenantTable
        self.url = 'tenancy:tenant_list'


class ContactIndex(SearchMixin):
    def __init__(self):
        self.model = Contact
        self.queryset = Contact.objects.prefetch_related('group', 'assignments').annotate(
            assignment_count=count_related(ContactAssignment, 'contact')
        )
        self.filterset = tenancy.filtersets.ContactFilterSet
        self.table = tenancy.tables.ContactTable
        self.url = 'tenancy:contact_list'


TENANCY_SEARCH_TYPES = {
    'tenant': TenantIndex(),
    'contact': ContactIndex(),
}
