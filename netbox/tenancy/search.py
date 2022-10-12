import tenancy.filtersets
import tenancy.tables
from netbox.search import SearchIndex, register_search
from tenancy.models import Contact, ContactAssignment, Tenant
from utilities.utils import count_related


@register_search()
class ContactIndex(SearchIndex):
    model = Contact
    fields = (
        ('name', 100),
        ('title', 300),
        ('phone', 300),
        ('email', 300),
        ('address', 300),
        ('link', 300),
        ('comments', 5000),
    )
    queryset = Contact.objects.prefetch_related('group', 'assignments').annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = tenancy.filtersets.ContactFilterSet


@register_search()
class TenantIndex(SearchIndex):
    model = Tenant
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
        ('comments', 5000),
    )
    queryset = Tenant.objects.prefetch_related('group')
    filterset = tenancy.filtersets.TenantFilterSet
