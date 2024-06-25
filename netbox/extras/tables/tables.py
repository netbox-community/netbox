import json

import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from extras.models import *
from netbox.constants import EMPTY_TABLE_TEXT
from netbox.tables import BaseTable, NetBoxTable, columns

__all__ = (
    'BookmarkTable',
    'ConfigContextTable',
    'ConfigTemplateTable',
    'CustomFieldChoiceSetTable',
    'CustomFieldTable',
    'CustomLinkTable',
    'EventRuleTable',
    'ExportTemplateTable',
    'ImageAttachmentTable',
    'JournalEntryTable',
    'SavedFilterTable',
    'ReportResultsTable',
    'ScriptResultsTable',
    'TaggedItemTable',
    'TagTable',
    'WebhookTable',
)

IMAGEATTACHMENT_IMAGE = '''
{% if record.image %}
  <a class="image-preview" href="{{ record.image.url }}" target="_blank">{{ record }}</a>
{% else %}
  &mdash;
{% endif %}
'''


class CustomFieldTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types')
    )
    required = columns.BooleanColumn(
        verbose_name=_('Required')
    )
    ui_visible = columns.ChoiceFieldColumn(
        verbose_name=_('Visible')
    )
    ui_editable = columns.ChoiceFieldColumn(
        verbose_name=_('Editable')
    )
    description = columns.MarkdownColumn(
        verbose_name=_('Description')
    )
    related_object_type = columns.ContentTypeColumn(
        verbose_name=_('Related Object Type')
    )
    choice_set = tables.Column(
        linkify=True,
        verbose_name=_('Choice Set')
    )
    choices = columns.ChoicesColumn(
        max_items=10,
        orderable=False,
        verbose_name=_('Choices')
    )
    is_cloneable = columns.BooleanColumn(
        verbose_name=_('Is Cloneable'),
    )
    validation_minimum = tables.Column(
        verbose_name=_('Minimum Value'),
    )
    validation_maximum = tables.Column(
        verbose_name=_('Maximum Value'),
    )
    validation_regex = tables.Column(
        verbose_name=_('Validation Regex'),
    )
    validation_unique = columns.BooleanColumn(
        verbose_name=_('Validate Uniqueness'),
    )

    class Meta(NetBoxTable.Meta):
        model = CustomField
        fields = (
            'pk', 'id', 'name', 'object_types', 'label', 'type', 'related_object_type', 'group_name', 'required',
            'default', 'description', 'search_weight', 'filter_logic', 'ui_visible', 'ui_editable', 'is_cloneable',
            'weight', 'choice_set', 'choices', 'validation_minimum', 'validation_maximum', 'validation_regex',
            'validation_unique', 'comments', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'object_types', 'label', 'group_name', 'type', 'required', 'description')


class CustomFieldChoiceSetTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    base_choices = columns.ChoiceFieldColumn()
    extra_choices = tables.TemplateColumn(
        template_code="""{% for k, v in value.items %}{{ v }}{% if not forloop.last %}, {% endif %}{% endfor %}"""
    )
    choices = columns.ChoicesColumn(
        max_items=10,
        orderable=False
    )
    choice_count = tables.TemplateColumn(
        accessor=tables.A('extra_choices'),
        template_code='{{ value|length }}',
        orderable=False,
        verbose_name=_('Count')
    )
    order_alphabetically = columns.BooleanColumn(
        verbose_name=_('Order Alphabetically'),
    )

    class Meta(NetBoxTable.Meta):
        model = CustomFieldChoiceSet
        fields = (
            'pk', 'id', 'name', 'description', 'base_choices', 'extra_choices', 'choice_count', 'choices',
            'order_alphabetically', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'base_choices', 'choice_count', 'description')


class CustomLinkTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    new_window = columns.BooleanColumn(
        verbose_name=_('New Window'),
    )

    class Meta(NetBoxTable.Meta):
        model = CustomLink
        fields = (
            'pk', 'id', 'name', 'object_types', 'enabled', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'object_types', 'enabled', 'group_name', 'button_class', 'new_window')


class ExportTemplateTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )
    as_attachment = columns.BooleanColumn(
        verbose_name=_('As Attachment'),
    )
    data_source = tables.Column(
        verbose_name=_('Data Source'),
        linkify=True
    )
    data_file = tables.Column(
        verbose_name=_('Data File'),
        linkify=True
    )
    is_synced = columns.BooleanColumn(
        orderable=False,
        verbose_name=_('Synced')
    )

    class Meta(NetBoxTable.Meta):
        model = ExportTemplate
        fields = (
            'pk', 'id', 'name', 'object_types', 'description', 'mime_type', 'file_extension', 'as_attachment',
            'data_source', 'data_file', 'data_synced', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'object_types', 'description', 'mime_type', 'file_extension', 'as_attachment', 'is_synced',
        )


class ImageAttachmentTable(NetBoxTable):
    id = tables.Column(
        verbose_name=_('ID'),
        linkify=False
    )
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Type'),
    )
    parent = tables.Column(
        verbose_name=_('Parent'),
        linkify=True
    )
    image = tables.TemplateColumn(
        verbose_name=_('Image'),
        template_code=IMAGEATTACHMENT_IMAGE,
    )
    size = tables.Column(
        orderable=False,
        verbose_name=_('Size (Bytes)')
    )

    class Meta(NetBoxTable.Meta):
        model = ImageAttachment
        fields = (
            'pk', 'object_type', 'parent', 'image', 'name', 'image_height', 'image_width', 'size', 'created',
            'last_updated',
        )
        default_columns = ('object_type', 'parent', 'image', 'name', 'size', 'created')


class SavedFilterTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    shared = columns.BooleanColumn(
        verbose_name=_('Shared'),
    )

    def value_parameters(self, value):
        return json.dumps(value)

    class Meta(NetBoxTable.Meta):
        model = SavedFilter
        fields = (
            'pk', 'id', 'name', 'slug', 'object_types', 'description', 'user', 'weight', 'enabled', 'shared',
            'created', 'last_updated', 'parameters'
        )
        default_columns = (
            'pk', 'name', 'object_types', 'user', 'description', 'enabled', 'shared',
        )


class BookmarkTable(NetBoxTable):
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Types'),
    )
    object = tables.Column(
        verbose_name=_('Object'),
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = Bookmark
        fields = ('pk', 'object', 'object_type', 'created')
        default_columns = ('object', 'object_type', 'created')


class WebhookTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    ssl_validation = columns.BooleanColumn(
        verbose_name=_('SSL Validation')
    )
    tags = columns.TagColumn(
        url_name='extras:webhook_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Webhook
        fields = (
            'pk', 'id', 'name', 'http_method', 'payload_url', 'http_content_type', 'secret', 'ssl_verification',
            'ca_file_path', 'description', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'http_method', 'payload_url', 'description',
        )


class EventRuleTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    action_type = tables.Column(
        verbose_name=_('Type'),
    )
    action_object = tables.Column(
        linkify=True,
        verbose_name=_('Object'),
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    type_create = columns.BooleanColumn(
        verbose_name=_('Create')
    )
    type_update = columns.BooleanColumn(
        verbose_name=_('Update')
    )
    type_delete = columns.BooleanColumn(
        verbose_name=_('Delete')
    )
    type_job_start = columns.BooleanColumn(
        verbose_name=_('Job Start')
    )
    type_job_end = columns.BooleanColumn(
        verbose_name=_('Job End')
    )
    tags = columns.TagColumn(
        url_name='extras:webhook_list'
    )

    class Meta(NetBoxTable.Meta):
        model = EventRule
        fields = (
            'pk', 'id', 'name', 'enabled', 'description', 'action_type', 'action_object', 'object_types',
            'type_create', 'type_update', 'type_delete', 'type_job_start', 'type_job_end', 'tags', 'created',
            'last_updated',
        )
        default_columns = (
            'pk', 'name', 'enabled', 'action_type', 'action_object', 'object_types', 'type_create', 'type_update',
            'type_delete', 'type_job_start', 'type_job_end',
        )


class TagTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    color = columns.ColorColumn(
        verbose_name=_('Color'),
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )

    class Meta(NetBoxTable.Meta):
        model = Tag
        fields = (
            'pk', 'id', 'name', 'items', 'slug', 'color', 'description', 'object_types', 'created', 'last_updated',
            'actions',
        )
        default_columns = ('pk', 'name', 'items', 'slug', 'color', 'description')


class TaggedItemTable(NetBoxTable):
    id = tables.Column(
        verbose_name=_('ID'),
        linkify=lambda record: record.content_object.get_absolute_url(),
        accessor='content_object__id'
    )
    content_type = columns.ContentTypeColumn(
        verbose_name=_('Type')
    )
    content_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name=_('Object')
    )
    actions = columns.ActionsColumn(
        actions=()
    )

    class Meta(NetBoxTable.Meta):
        model = TaggedItem
        fields = ('id', 'content_type', 'content_object')


class ConfigContextTable(NetBoxTable):
    data_source = tables.Column(
        verbose_name=_('Data Source'),
        linkify=True
    )
    data_file = tables.Column(
        verbose_name=_('Data File'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    is_active = columns.BooleanColumn(
        verbose_name=_('Active')
    )
    is_synced = columns.BooleanColumn(
        orderable=False,
        verbose_name=_('Synced')
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
        verbose_name=_('Name'),
        linkify=True
    )
    data_source = tables.Column(
        verbose_name=_('Data Source'),
        linkify=True
    )
    data_file = tables.Column(
        verbose_name=_('Data File'),
        linkify=True
    )
    is_synced = columns.BooleanColumn(
        orderable=False,
        verbose_name=_('Synced')
    )
    tags = columns.TagColumn(
        url_name='extras:configtemplate_list'
    )
    role_count = columns.LinkedCountColumn(
        viewname='dcim:devicerole_list',
        url_params={'config_template_id': 'pk'},
        verbose_name=_('Device Roles')
    )
    platform_count = columns.LinkedCountColumn(
        viewname='dcim:platform_list',
        url_params={'config_template_id': 'pk'},
        verbose_name=_('Platforms')
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'config_template_id': 'pk'},
        verbose_name=_('Devices')
    )
    vm_count = columns.LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'config_template_id': 'pk'},
        verbose_name=_('Virtual Machines')
    )

    class Meta(NetBoxTable.Meta):
        model = ConfigTemplate
        fields = (
            'pk', 'id', 'name', 'description', 'data_source', 'data_file', 'data_synced', 'role_count',
            'platform_count', 'device_count', 'vm_count', 'created', 'last_updated', 'tags',
        )
        default_columns = (
            'pk', 'name', 'description', 'is_synced', 'device_count', 'vm_count',
        )


class JournalEntryTable(NetBoxTable):
    created = columns.DateTimeColumn(
        verbose_name=_('Created'),
        timespec='minutes',
        linkify=True
    )
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Type')
    )
    assigned_object = tables.Column(
        linkify=True,
        orderable=False,
        verbose_name=_('Object')
    )
    kind = columns.ChoiceFieldColumn(
        verbose_name=_('Kind'),
    )
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments'),
    )
    comments_short = tables.TemplateColumn(
        accessor=tables.A('comments'),
        template_code='{{ value|markdown|truncatewords_html:50 }}',
        verbose_name=_('Comments (Short)')
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


class ScriptResultsTable(BaseTable):
    index = tables.Column(
        verbose_name=_('Line')
    )
    time = tables.Column(
        verbose_name=_('Time')
    )
    status = tables.TemplateColumn(
        template_code="""{% load log_levels %}{% log_level record.status %}""",
        verbose_name=_('Level')
    )
    object = tables.Column(
        verbose_name=_('Object')
    )
    message = columns.MarkdownColumn(
        verbose_name=_('Message')
    )

    class Meta(BaseTable.Meta):
        empty_text = _(EMPTY_TABLE_TEXT)
        fields = (
            'index', 'time', 'status', 'object', 'message',
        )
        default_columns = (
            'index', 'time', 'status', 'object', 'message',
        )

    def render_object(self, value, record):
        return format_html("<a href='{}'>{}</a>", record['url'], value)

    def render_url(self, value):
        return format_html("<a href='{}'>{}</a>", value, value)


class ReportResultsTable(BaseTable):
    index = tables.Column(
        verbose_name=_('Line')
    )
    method = tables.Column(
        verbose_name=_('Method')
    )
    time = tables.Column(
        verbose_name=_('Time')
    )
    status = tables.TemplateColumn(
        template_code="""{% load log_levels %}{% log_level record.status %}""",
        verbose_name=_('Level')
    )
    object = tables.Column(
        verbose_name=_('Object')
    )
    url = tables.Column(
        verbose_name=_('URL')
    )
    message = columns.MarkdownColumn(
        verbose_name=_('Message')
    )

    class Meta(BaseTable.Meta):
        empty_text = _(EMPTY_TABLE_TEXT)
        fields = (
            'index', 'method', 'time', 'status', 'object', 'url', 'message',
        )

    def render_object(self, value, record):
        return format_html("<a href='{}'>{}</a>", record['url'], value)

    def render_url(self, value):
        return format_html("<a href='{}'>{}</a>", value, value)
