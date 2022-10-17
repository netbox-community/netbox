from netbox.search import SearchIndex, register_search
from utilities.utils import count_related
from . import filtersets, models


@register_search()
class ContactIndex(SearchIndex):
    model = models.Contact
    fields = (
        ('name', 100),
        ('title', 300),
        ('phone', 300),
        ('email', 300),
        ('address', 300),
        ('link', 300),
        ('comments', 5000),
    )
    queryset = models.Contact.objects.prefetch_related('group', 'assignments').annotate(
        assignment_count=count_related(models.ContactAssignment, 'contact')
    )
    filterset = filtersets.ContactFilterSet


@register_search()
class ContactGroupIndex(SearchIndex):
    model = models.ContactGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class ContactRoleIndex(SearchIndex):
    model = models.ContactRole
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search()
class TenantIndex(SearchIndex):
    model = models.Tenant
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
        ('comments', 5000),
    )
    queryset = models.Tenant.objects.prefetch_related('group')
    filterset = filtersets.TenantFilterSet


@register_search()
class TenantGroupIndex(SearchIndex):
    model = models.TenantGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
