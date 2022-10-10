import tenancy.filtersets
import tenancy.tables
from netbox.search.models import SearchMixin
from netbox.search import register_search
from tenancy.models import Contact, ContactAssignment, Tenant
from utilities.utils import count_related


@register_search(Tenant)
class TenantIndex(SearchMixin):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = tenancy.filtersets.TenantFilterSet
    table = tenancy.tables.TenantTable
    url = 'tenancy:tenant_list'
    choice_header = 'Tenancy'


@register_search(Contact)
class ContactIndex(SearchMixin):
    queryset = Contact.objects.prefetch_related('group', 'assignments').annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = tenancy.filtersets.ContactFilterSet
    table = tenancy.tables.ContactTable
    url = 'tenancy:contact_list'
    choice_header = 'Tenancy'
