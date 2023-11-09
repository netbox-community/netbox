from netbox.search import SearchIndex, register_search
from . import models


@register_search
class ContactIndex(SearchIndex):
    model = models.Contact
    fields = (
        ('name', 100),
        ('title', 300),
        ('phone', 300),
        ('email', 300),
        ('address', 300),
        ('link', 300),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('group', 'title', 'phone', 'email', 'description')


@register_search
class ContactGroupIndex(SearchIndex):
    model = models.ContactGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class ContactRoleIndex(SearchIndex):
    model = models.ContactRole
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class TenantIndex(SearchIndex):
    model = models.Tenant
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('group', 'description')


@register_search
class TenantGroupIndex(SearchIndex):
    model = models.TenantGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)
