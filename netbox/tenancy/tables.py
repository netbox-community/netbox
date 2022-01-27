import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from utilities.tables import linkify_phone
from .models import *

__all__ = (
    'ContactAssignmentTable',
    'ContactGroupTable',
    'ContactRoleTable',
    'ContactTable',
    'TenantColumn',
    'TenantGroupTable',
    'TenantTable',
)


#
# Table columns
#

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


#
# Tenants
#

class TenantGroupTable(NetBoxTable):
    name = columns.MPTTColumn(
        linkify=True
    )
    tenant_count = columns.LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group_id': 'pk'},
        verbose_name='Tenants'
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenantgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = TenantGroup
        fields = (
            'pk', 'id', 'name', 'tenant_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'tenant_count', 'description')


class TenantTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Tenant
        fields = ('pk', 'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'group', 'description')


#
# Contacts
#

class ContactGroupTable(NetBoxTable):
    name = columns.MPTTColumn(
        linkify=True
    )
    contact_count = columns.LinkedCountColumn(
        viewname='tenancy:contact_list',
        url_params={'role_id': 'pk'},
        verbose_name='Contacts'
    )
    tags = columns.TagColumn(
        url_name='tenancy:contactgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ContactGroup
        fields = (
            'pk', 'name', 'contact_count', 'description', 'slug', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'contact_count', 'description')


class ContactRoleTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = ContactRole
        fields = ('pk', 'name', 'description', 'slug', 'created', 'last_updated', 'actions')
        default_columns = ('pk', 'name', 'description')


class ContactTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    phone = tables.Column(
        linkify=linkify_phone,
    )
    comments = columns.MarkdownColumn()
    assignment_count = tables.Column(
        verbose_name='Assignments'
    )
    tags = columns.TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Contact
        fields = (
            'pk', 'name', 'group', 'title', 'phone', 'email', 'address', 'comments', 'assignment_count', 'tags',
            'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'group', 'assignment_count', 'title', 'phone', 'email')


class ContactAssignmentTable(NetBoxTable):
    content_type = columns.ContentTypeColumn(
        verbose_name='Object Type'
    )
    object = tables.Column(
        linkify=True,
        orderable=False
    )
    contact = tables.Column(
        linkify=True
    )
    role = tables.Column(
        linkify=True
    )
    actions = columns.ActionsColumn(
        sequence=('edit', 'delete')
    )

    class Meta(NetBoxTable.Meta):
        model = ContactAssignment
        fields = ('pk', 'content_type', 'object', 'contact', 'role', 'priority', 'actions')
        default_columns = ('pk', 'content_type', 'object', 'contact', 'role', 'priority')
