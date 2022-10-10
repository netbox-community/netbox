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
        ('title', 200),
        ('phone', 200),
        ('email', 200),
        ('address', 200),
        ('link', 300),
        ('comments', 1000),
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
        ('slug', 100),
        ('description', 500),
        ('comments', 1000),
    )
    queryset = Tenant.objects.prefetch_related('group')
    filterset = tenancy.filtersets.TenantFilterSet
