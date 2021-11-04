import django_tables2 as tables

from utilities.tables import (
    BaseTable, ButtonsColumn, ContentTypeColumn, LinkedCountColumn, MarkdownColumn, MPTTColumn, TagColumn, ToggleColumn,
)
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

class TenantGroupTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    tenant_count = LinkedCountColumn(
        viewname='tenancy:tenant_list',
        url_params={'group_id': 'pk'},
        verbose_name='Tenants'
    )
    tags = TagColumn(
        url_name='tenancy:tenantgroup_list'
    )
    actions = ButtonsColumn(TenantGroup)

    class Meta(BaseTable.Meta):
        model = TenantGroup
        fields = ('pk', 'id', 'name', 'tenant_count', 'description', 'slug', 'tags', 'actions')
        default_columns = ('pk', 'name', 'tenant_count', 'description', 'actions')


class TenantTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(BaseTable.Meta):
        model = Tenant
        fields = ('pk', 'id', 'name', 'slug', 'group', 'description', 'comments', 'tags')
        default_columns = ('pk', 'name', 'group', 'description')


#
# Contacts
#

class ContactGroupTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    contact_count = LinkedCountColumn(
        viewname='tenancy:contact_list',
        url_params={'role_id': 'pk'},
        verbose_name='Contacts'
    )
    tags = TagColumn(
        url_name='tenancy:contactgroup_list'
    )
    actions = ButtonsColumn(ContactGroup)

    class Meta(BaseTable.Meta):
        model = ContactGroup
        fields = ('pk', 'name', 'contact_count', 'description', 'slug', 'tags', 'actions')
        default_columns = ('pk', 'name', 'contact_count', 'description', 'actions')


class ContactRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    actions = ButtonsColumn(ContactRole)

    class Meta(BaseTable.Meta):
        model = ContactRole
        fields = ('pk', 'name', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'description', 'actions')


class ContactTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    comments = MarkdownColumn()
    assignment_count = tables.Column(
        verbose_name='Assignments'
    )
    tags = TagColumn(
        url_name='tenancy:tenant_list'
    )

    class Meta(BaseTable.Meta):
        model = Contact
        fields = ('pk', 'name', 'group', 'title', 'phone', 'email', 'address', 'comments', 'assignment_count', 'tags')
        default_columns = ('pk', 'name', 'group', 'assignment_count', 'title', 'phone', 'email')


class ContactAssignmentTable(BaseTable):
    pk = ToggleColumn()
    content_type = ContentTypeColumn(
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
    actions = ButtonsColumn(
        model=ContactAssignment,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = ContactAssignment
        fields = ('pk', 'content_type', 'object', 'contact', 'role', 'priority', 'actions')
        default_columns = ('pk', 'content_type', 'object', 'contact', 'role', 'priority', 'actions')
