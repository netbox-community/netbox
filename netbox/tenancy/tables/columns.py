import django_tables2 as tables

from netbox.tables import columns

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
    template_code = """
    {% if record.tenant %}
        <a href="{{ record.tenant.get_absolute_url }}" title="{{ record.tenant.description }}">{{ record.tenant }}</a>
    {% elif record.vrf.tenant %}
        <a href="{{ record.vrf.tenant.get_absolute_url }}" title="{{ record.vrf.tenant.description }}">{{ record.vrf.tenant }}</a>*
    {% else %}
        &mdash;
    {% endif %}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None


class TenantGroupColumn(tables.TemplateColumn):
    """
    Include the tenant group description.
    """
    template_code = """
    {% if record.tenant and record.tenant.group %}
        <a href="{{ record.tenant.group.get_absolute_url }}" title="{{ record.tenant.group.description }}">{{ record.tenant.group }}</a>
    {% elif record.vrf.tenant and record.vrf.tenant.group %}
        <a href="{{ record.vrf.tenant.group.get_absolute_url }}" title="{{ record.vrf.tenant.group.description }}">{{ record.vrf.tenant.group }}</a>*
    {% else %}
        &mdash;
    {% endif %}
    """

    def __init__(self, accessor=tables.A('tenant__group'), *args, **kwargs):
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = 'Tenant Group'

        super().__init__(template_code=self.template_code, accessor=accessor, *args, **kwargs)

    def value(self, value):
        return str(value) if value else None


class TenancyColumnsMixin(tables.Table):
    tenant_group = TenantGroupColumn()
    tenant = TenantColumn()


class ContactsColumnMixin(tables.Table):
    contacts = columns.ManyToManyColumn(
        linkify_item=True,
        transform=lambda obj: obj.contact.name
    )
