import django_tables2 as tables
from django.conf import settings

from netbox.tables import NetBoxTable, columns
from .models import *

__all__ = (
    'ConfigContextTable',
    'CustomFieldTable',
    'CustomLinkTable',
    'ExportTemplateTable',
    'JournalEntryTable',
    'ObjectChangeTable',
    'ObjectJournalTable',
    'TaggedItemTable',
    'TagTable',
    'WebhookTable',
)

CONFIGCONTEXT_ACTIONS = """
{% if perms.extras.change_configcontext %}
    <a href="{% url 'extras:configcontext_edit' pk=record.pk %}" class="btn btn-sm btn-warning"><i class="mdi mdi-pencil" aria-hidden="true"></i></a>
{% endif %}
{% if perms.extras.delete_configcontext %}
    <a href="{% url 'extras:configcontext_delete' pk=record.pk %}" class="btn btn-sm btn-danger"><i class="mdi mdi-trash-can-outline" aria-hidden="true"></i></a>
{% endif %}
"""

OBJECTCHANGE_OBJECT = """
{% if record.changed_object and record.changed_object.get_absolute_url %}
    <a href="{{ record.changed_object.get_absolute_url }}">{{ record.object_repr }}</a>
{% else %}
    {{ record.object_repr }}
{% endif %}
"""

OBJECTCHANGE_REQUEST_ID = """
<a href="{% url 'extras:objectchange_list' %}?request_id={{ value }}">{{ value }}</a>
"""


#
# Custom fields
#

class CustomFieldTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    required = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = CustomField
        fields = (
            'pk', 'id', 'name', 'content_types', 'label', 'type', 'required', 'weight', 'default',
            'description', 'filter_logic', 'choices', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'content_types', 'label', 'type', 'required', 'description')


#
# Custom links
#

class CustomLinkTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_type = columns.ContentTypeColumn()
    enabled = columns.BooleanColumn()
    new_window = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = CustomLink
        fields = (
            'pk', 'id', 'name', 'content_type', 'enabled', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'content_type', 'enabled', 'group_name', 'button_class', 'new_window')


#
# Export templates
#

class ExportTemplateTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_type = columns.ContentTypeColumn()
    as_attachment = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = ExportTemplate
        fields = (
            'pk', 'id', 'name', 'content_type', 'description', 'mime_type', 'file_extension', 'as_attachment',
            'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'content_type', 'description', 'mime_type', 'file_extension', 'as_attachment',
        )


#
# Webhooks
#

class WebhookTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    enabled = columns.BooleanColumn()
    type_create = columns.BooleanColumn(
        verbose_name='Create'
    )
    type_update = columns.BooleanColumn(
        verbose_name='Update'
    )
    type_delete = columns.BooleanColumn(
        verbose_name='Delete'
    )
    ssl_validation = columns.BooleanColumn(
        verbose_name='SSL Validation'
    )

    class Meta(NetBoxTable.Meta):
        model = Webhook
        fields = (
            'pk', 'id', 'name', 'content_types', 'enabled', 'type_create', 'type_update', 'type_delete', 'http_method',
            'payload_url', 'secret', 'ssl_validation', 'ca_file_path', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'content_types', 'enabled', 'type_create', 'type_update', 'type_delete', 'http_method',
            'payload_url',
        )


#
# Tags
#

class TagTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    color = columns.ColorColumn()

    class Meta(NetBoxTable.Meta):
        model = Tag
        fields = ('pk', 'id', 'name', 'items', 'slug', 'color', 'description', 'created', 'last_updated', 'actions')
        default_columns = ('pk', 'name', 'items', 'slug', 'color', 'description')


class TaggedItemTable(NetBoxTable):
    id = tables.Column(
        verbose_name='ID',
        linkify=lambda record: record.content_object.get_absolute_url(),
        accessor='content_object__id'
    )
    content_type = columns.ContentTypeColumn(
        verbose_name='Type'
    )
    content_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object'
    )

    class Meta(NetBoxTable.Meta):
        model = TaggedItem
        fields = ('id', 'content_type', 'content_object')


class ConfigContextTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    is_active = columns.BooleanColumn(
        verbose_name='Active'
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigContext
        fields = (
            'pk', 'id', 'name', 'weight', 'is_active', 'description', 'regions', 'sites', 'roles',
            'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'weight', 'is_active', 'description')


class ObjectChangeTable(NetBoxTable):
    time = tables.DateTimeColumn(
        linkify=True,
        format=settings.SHORT_DATETIME_FORMAT
    )
    action = columns.ChoiceFieldColumn()
    changed_object_type = columns.ContentTypeColumn(
        verbose_name='Type'
    )
    object_repr = tables.TemplateColumn(
        template_code=OBJECTCHANGE_OBJECT,
        verbose_name='Object'
    )
    request_id = tables.TemplateColumn(
        template_code=OBJECTCHANGE_REQUEST_ID,
        verbose_name='Request ID'
    )
    actions = columns.ActionsColumn(sequence=())

    class Meta(NetBoxTable.Meta):
        model = ObjectChange
        fields = ('id', 'time', 'user_name', 'action', 'changed_object_type', 'object_repr', 'request_id')


class ObjectJournalTable(NetBoxTable):
    """
    Used for displaying a set of JournalEntries within the context of a single object.
    """
    created = tables.DateTimeColumn(
        linkify=True,
        format=settings.SHORT_DATETIME_FORMAT
    )
    kind = columns.ChoiceFieldColumn()
    comments = tables.TemplateColumn(
        template_code='{% load helpers %}{{ value|render_markdown|truncatewords_html:50 }}'
    )

    class Meta(NetBoxTable.Meta):
        model = JournalEntry
        fields = ('id', 'created', 'created_by', 'kind', 'comments', 'actions')


class JournalEntryTable(ObjectJournalTable):
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name='Object type'
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object'
    )
    comments = columns.MarkdownColumn()

    class Meta(NetBoxTable.Meta):
        model = JournalEntry
        fields = (
            'pk', 'id', 'created', 'created_by', 'assigned_object_type', 'assigned_object', 'kind',
            'comments', 'actions'
        )
        default_columns = (
            'pk', 'created', 'created_by', 'assigned_object_type', 'assigned_object', 'kind', 'comments'
        )
