import django_tables2 as tables
from django.conf import settings

from extras.models import *
from netbox.tables import NetBoxTable, columns
from .template_code import *

__all__ = (
    'ConfigContextTable',
    'CustomFieldTable',
    'CustomLinkTable',
    'ExportTemplateTable',
    'JournalEntryTable',
    'ObjectChangeTable',
    'TaggedItemTable',
    'TagTable',
    'WebhookTable',
)


#
# Custom fields
#

class CustomFieldTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    required = columns.BooleanColumn()
    ui_visibility = columns.ChoiceFieldColumn(verbose_name="UI visibility")

    class Meta(NetBoxTable.Meta):
        model = CustomField
        fields = (
            'pk', 'id', 'name', 'content_types', 'label', 'type', 'group_name', 'required', 'weight', 'default',
            'description', 'filter_logic', 'ui_visibility', 'choices', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'content_types', 'label', 'group_name', 'type', 'required', 'description')


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
    actions = columns.ActionsColumn(
        actions=()
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
            'pk', 'id', 'name', 'weight', 'is_active', 'description', 'regions', 'sites', 'locations', 'roles',
            'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'weight', 'is_active', 'description')


class ObjectChangeTable(NetBoxTable):
    time = tables.DateTimeColumn(
        linkify=True,
        format=settings.SHORT_DATETIME_FORMAT
    )
    user_name = tables.Column(
        verbose_name='Username'
    )
    full_name = tables.TemplateColumn(
        accessor=tables.A('user'),
        template_code=OBJECTCHANGE_FULL_NAME,
        verbose_name='Full Name',
        orderable=False
    )
    action = columns.ChoiceFieldColumn()
    changed_object_type = columns.ContentTypeColumn(
        verbose_name='Type'
    )
    object_repr = tables.TemplateColumn(
        accessor=tables.A('changed_object'),
        template_code=OBJECTCHANGE_OBJECT,
        verbose_name='Object'
    )
    request_id = tables.TemplateColumn(
        template_code=OBJECTCHANGE_REQUEST_ID,
        verbose_name='Request ID'
    )
    actions = columns.ActionsColumn(
        actions=()
    )

    class Meta(NetBoxTable.Meta):
        model = ObjectChange
        fields = (
            'pk', 'id', 'time', 'user_name', 'full_name', 'action', 'changed_object_type', 'object_repr', 'request_id',
            'actions',
        )


class JournalEntryTable(NetBoxTable):
    created = tables.DateTimeColumn(
        linkify=True,
        format=settings.SHORT_DATETIME_FORMAT
    )
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name='Object type'
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name='Object'
    )
    kind = columns.ChoiceFieldColumn()
    comments = columns.MarkdownColumn()
    comments_short = tables.TemplateColumn(
        accessor=tables.A('comments'),
        template_code='{{ value|markdown|truncatewords_html:50 }}',
        verbose_name='Comments (Short)'
    )
    tags = columns.TagColumn(
        url_name='extras:journalentry_list'
    )

    class Meta(NetBoxTable.Meta):
        model = JournalEntry
        fields = (
            'pk', 'id', 'created', 'created_by', 'assigned_object_type', 'assigned_object', 'kind', 'comments',
            'comments_short', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'created', 'created_by', 'assigned_object_type', 'assigned_object', 'kind', 'comments'
        )
