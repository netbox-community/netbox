import json

import django_tables2 as tables
from django.conf import settings

from extras.models import *
from netbox.tables import NetBoxTable, columns
from .template_code import *

__all__ = (
    'ConfigContextTable',
    'ConfigTemplateTable',
    'CustomFieldTable',
    'CustomLinkTable',
    'ExportTemplateTable',
    'JournalEntryTable',
    'ObjectChangeTable',
    'SavedFilterTable',
    'TaggedItemTable',
    'TagTable',
    'WebhookTable',
)


class CustomFieldTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    required = columns.BooleanColumn()
    ui_visibility = columns.ChoiceFieldColumn(verbose_name="UI visibility")
    is_cloneable = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = CustomField
        fields = (
            'pk', 'id', 'name', 'content_types', 'label', 'type', 'group_name', 'required', 'default', 'description',
            'search_weight', 'filter_logic', 'ui_visibility', 'is_cloneable', 'weight', 'choices', 'created',
            'last_updated',
        )
        default_columns = ('pk', 'name', 'content_types', 'label', 'group_name', 'type', 'required', 'description')


class CustomLinkTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    enabled = columns.BooleanColumn()
    new_window = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = CustomLink
        fields = (
            'pk', 'id', 'name', 'content_types', 'enabled', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'content_types', 'enabled', 'group_name', 'button_class', 'new_window')


class ExportTemplateTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    as_attachment = columns.BooleanColumn()
    data_source = tables.Column(
        linkify=True
    )
    data_file = tables.Column(
        linkify=True
    )
    is_synced = columns.BooleanColumn(
        verbose_name='Synced'
    )

    class Meta(NetBoxTable.Meta):
        model = ExportTemplate
        fields = (
            'pk', 'id', 'name', 'content_types', 'description', 'mime_type', 'file_extension', 'as_attachment',
            'data_source', 'data_file', 'data_synced', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'content_types', 'description', 'mime_type', 'file_extension', 'as_attachment', 'is_synced',
        )


class SavedFilterTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    content_types = columns.ContentTypesColumn()
    enabled = columns.BooleanColumn()
    shared = columns.BooleanColumn()

    def value_parameters(self, value):
        return json.dumps(value)

    class Meta(NetBoxTable.Meta):
        model = SavedFilter
        fields = (
            'pk', 'id', 'name', 'slug', 'content_types', 'description', 'user', 'weight', 'enabled', 'shared',
            'created', 'last_updated', 'parameters'
        )
        default_columns = (
            'pk', 'name', 'content_types', 'user', 'description', 'enabled', 'shared',
        )


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
    type_job_start = columns.BooleanColumn(
        verbose_name='Job start'
    )
    type_job_end = columns.BooleanColumn(
        verbose_name='Job end'
    )
    ssl_validation = columns.BooleanColumn(
        verbose_name='SSL Validation'
    )

    class Meta(NetBoxTable.Meta):
        model = Webhook
        fields = (
            'pk', 'id', 'name', 'content_types', 'enabled', 'type_create', 'type_update', 'type_delete',
            'type_job_start', 'type_job_end', 'http_method', 'payload_url', 'secret', 'ssl_validation', 'ca_file_path',
            'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'content_types', 'enabled', 'type_create', 'type_update', 'type_delete', 'type_job_start',
            'type_job_end', 'http_method', 'payload_url',
        )


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
    data_source = tables.Column(
        linkify=True
    )
    data_file = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )
    is_active = columns.BooleanColumn(
        verbose_name='Active'
    )
    is_synced = columns.BooleanColumn(
        verbose_name='Synced'
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigContext
        fields = (
            'pk', 'id', 'name', 'weight', 'is_active', 'is_synced', 'description', 'regions', 'sites', 'locations',
            'roles', 'platforms', 'cluster_types', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants',
            'data_source', 'data_file', 'data_synced', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'weight', 'is_active', 'is_synced', 'description')


class ConfigTemplateTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    data_source = tables.Column(
        linkify=True
    )
    data_file = tables.Column(
        linkify=True
    )
    is_synced = columns.BooleanColumn(
        verbose_name='Synced'
    )
    tags = columns.TagColumn(
        url_name='extras:configtemplate_list'
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigTemplate
        fields = (
            'pk', 'id', 'name', 'description', 'data_source', 'data_file', 'data_synced', 'created', 'last_updated',
            'tags',
        )
        default_columns = (
            'pk', 'name', 'description', 'is_synced',
        )


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
        verbose_name='Object',
        orderable=False
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
