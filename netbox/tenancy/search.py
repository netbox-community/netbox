import tenancy.filtersets
import tenancy.tables
from netbox.search import SearchIndex, register_search
from tenancy.models import Contact, ContactAssignment, Tenant
from utilities.utils import count_related


@register_search()
class TenantIndex(SearchIndex):
    model = Tenant
    queryset = Tenant.objects.prefetch_related('group')
    filterset = tenancy.filtersets.TenantFilterSet
    table = tenancy.tables.TenantTable
    url = 'tenancy:tenant_list'


@register_search()
class ContactIndex(SearchIndex):
    model = Contact
    queryset = Contact.objects.prefetch_related('group', 'assignments').annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = tenancy.filtersets.ContactFilterSet
    table = tenancy.tables.ContactTable
    url = 'tenancy:contact_list'
