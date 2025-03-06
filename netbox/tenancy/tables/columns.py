from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from netbox.tables import columns
from .template_code import *

__all__ = (
    'ContactsColumnMixin',
    'TenantColumn',
    'TenantGroupColumn',
    'TenancyColumnsMixin',
)


class TenantColumn(tables.TemplateColumn):
    """
    Include the tenant description.
    """
    template_code = TENANT_COLUMN

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None


class TenantGroupColumn(tables.TemplateColumn):
    """
    Include the tenant group description.
    """
    template_code = TENANT_GROUP_COLUMN

    def __init__(self, accessor=tables.A('tenant__group'), *args, **kwargs):
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = _('Tenant Group')

        super().__init__(template_code=self.template_code, accessor=accessor, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None


class TenancyColumnsMixin(tables.Table):
    tenant_group = TenantGroupColumn(
        verbose_name=_('Tenant Group'),
    )
    tenant = TenantColumn(
        verbose_name=_('Tenant'),
    )


class ContactsColumnMixin(tables.Table):
    contacts = columns.ManyToManyColumn(
        verbose_name=_('Contacts'),
        linkify_item=True,
        transform=lambda obj: obj.contact.name
    )
