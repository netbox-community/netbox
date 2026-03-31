from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs, panels
from utilities.data import resolve_attr_path

__all__ = (
    'ConfigContextAssignmentPanel',
    'ConfigContextPanel',
    'ConfigContextProfilePanel',
    'ConfigTemplatePanel',
    'CustomFieldBehaviorPanel',
    'CustomFieldChoiceSetChoicesPanel',
    'CustomFieldChoiceSetPanel',
    'CustomFieldObjectTypesPanel',
    'CustomFieldPanel',
    'CustomFieldRelatedObjectsPanel',
    'CustomFieldValidationPanel',
    'CustomFieldsPanel',
    'CustomLinkPanel',
    'EventRuleActionPanel',
    'EventRuleEventTypesPanel',
    'EventRulePanel',
    'ExportTemplatePanel',
    'ImageAttachmentFilePanel',
    'ImageAttachmentImagePanel',
    'ImageAttachmentPanel',
    'ImageAttachmentsPanel',
    'JournalEntryPanel',
    'NotificationGroupGroupsPanel',
    'NotificationGroupPanel',
    'NotificationGroupUsersPanel',
    'ObjectTypesPanel',
    'SavedFilterObjectTypesPanel',
    'SavedFilterPanel',
    'TableConfigColumnsPanel',
    'TableConfigOrderingPanel',
    'TableConfigPanel',
    'TagItemTypesPanel',
    'TagObjectTypesPanel',
    'TagPanel',
    'TagsPanel',
    'WebhookHTTPPanel',
    'WebhookPanel',
    'WebhookSSLPanel',
)


#
# Generic panels
#

class CustomFieldsPanel(panels.ObjectPanel):
    """
    A panel showing the value of all custom fields defined on an object.
    """
    template_name = 'extras/panels/custom_fields.html'
    title = _('Custom Fields')

    def get_context(self, context):
        obj = resolve_attr_path(context, self.accessor)
        return {
            **super().get_context(context),
            'custom_fields': obj.get_custom_fields_by_group(),
        }

    def render(self, context):
        ctx = self.get_context(context)
        # Hide the panel if no custom fields exist
        if not ctx['custom_fields']:
            return ''
        return render_to_string(self.template_name, self.get_context(context))


class ImageAttachmentsPanel(panels.ObjectsTablePanel):
    """
    A panel showing all images attached to the object.
    """
    actions = [
        actions.AddObject(
            'extras.imageattachment',
            url_params={
                'object_type': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'object_id': lambda ctx: ctx['object'].pk,
                'return_url': lambda ctx: ctx['object'].get_absolute_url(),
            },
            label=_('Attach an image'),
        ),
    ]

    def __init__(self, **kwargs):
        super().__init__(
            'extras.imageattachment',
            filters={
                'object_type_id': lambda ctx: ContentType.objects.get_for_model(ctx['object']).pk,
                'object_id': lambda ctx: ctx['object'].pk,
            },
            **kwargs,
        )


class TagsPanel(panels.ObjectPanel):
    """
    A panel showing the tags assigned to the object.
    """
    template_name = 'extras/panels/tags.html'
    title = _('Tags')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'object': resolve_attr_path(context, self.accessor),
        }


class ObjectTypesPanel(panels.ObjectPanel):
    """
    A panel listing the object types assigned to the object.
    """
    template_name = 'extras/panels/object_types.html'
    title = _('Object Types')


#
# CustomField panels
#

class CustomFieldPanel(panels.ObjectAttributesPanel):
    title = _('Custom Field')

    name = attrs.TextAttr('name')
    type = attrs.TemplatedAttr('type', label=_('Type'), template_name='extras/customfield/attrs/type.html')
    label = attrs.TextAttr('label')
    group_name = attrs.TextAttr('group_name', label=_('Group name'))
    description = attrs.TextAttr('description')
    required = attrs.BooleanAttr('required')
    unique = attrs.BooleanAttr('unique', label=_('Must be unique'))
    is_cloneable = attrs.BooleanAttr('is_cloneable', label=_('Cloneable'))
    choice_set = attrs.TemplatedAttr(
        'choice_set',
        template_name='extras/customfield/attrs/choice_set.html',
    )
    default = attrs.TextAttr('default', label=_('Default value'))
    related_object_filter = attrs.TemplatedAttr(
        'related_object_filter',
        template_name='extras/customfield/attrs/related_object_filter.html',
    )


class CustomFieldBehaviorPanel(panels.ObjectAttributesPanel):
    title = _('Behavior')

    search_weight = attrs.TemplatedAttr(
        'search_weight',
        template_name='extras/customfield/attrs/search_weight.html',
    )
    filter_logic = attrs.ChoiceAttr('filter_logic')
    weight = attrs.NumericAttr('weight', label=_('Display weight'))
    ui_visible = attrs.ChoiceAttr('ui_visible', label=_('UI visible'))
    ui_editable = attrs.ChoiceAttr('ui_editable', label=_('UI editable'))


class CustomFieldValidationPanel(panels.ObjectAttributesPanel):
    title = _('Validation Rules')

    validation_minimum = attrs.NumericAttr('validation_minimum', label=_('Minimum value'))
    validation_maximum = attrs.NumericAttr('validation_maximum', label=_('Maximum value'))
    validation_regex = attrs.TextAttr(
        'validation_regex',
        label=_('Regular expression'),
        style='font-monospace',
    )


class CustomFieldObjectTypesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/object_types.html'
    title = _('Object Types')


class CustomFieldRelatedObjectsPanel(panels.ObjectPanel):
    template_name = 'extras/panels/customfield_related_objects.html'
    title = _('Related Objects')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'related_models': context.get('related_models'),
        }


#
# CustomFieldChoiceSet panels
#

class CustomFieldChoiceSetPanel(panels.ObjectAttributesPanel):
    title = _('Custom Field Choice Set')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    base_choices = attrs.ChoiceAttr('base_choices')
    order_alphabetically = attrs.BooleanAttr('order_alphabetically')
    choices_for = attrs.RelatedObjectListAttr('choices_for', linkify=True, label=_('Used by'))


class CustomFieldChoiceSetChoicesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/customfieldchoiceset_choices.html'

    def get_context(self, context):
        obj = context.get('object')
        total = len(obj.choices) if obj else 0
        return {
            **super().get_context(context),
            'title': f'{_("Choices")} ({total})',
            'choices': context.get('choices'),
        }


#
# CustomLink panels
#

class CustomLinkPanel(panels.ObjectAttributesPanel):
    title = _('Custom Link')

    name = attrs.TextAttr('name')
    enabled = attrs.BooleanAttr('enabled')
    group_name = attrs.TextAttr('group_name')
    weight = attrs.NumericAttr('weight')
    button_class = attrs.ChoiceAttr('button_class')
    new_window = attrs.BooleanAttr('new_window')


#
# ExportTemplate panels
#

class ExportTemplatePanel(panels.ObjectAttributesPanel):
    title = _('Export Template')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    mime_type = attrs.TextAttr('mime_type', label=_('MIME type'))
    file_name = attrs.TextAttr('file_name')
    file_extension = attrs.TextAttr('file_extension')
    as_attachment = attrs.BooleanAttr('as_attachment', label=_('Attachment'))


#
# SavedFilter panels
#

class SavedFilterPanel(panels.ObjectAttributesPanel):
    title = _('Saved Filter')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    user = attrs.TextAttr('user')
    enabled = attrs.BooleanAttr('enabled')
    shared = attrs.BooleanAttr('shared')
    weight = attrs.NumericAttr('weight')


class SavedFilterObjectTypesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/savedfilter_object_types.html'
    title = _('Assigned Models')


#
# TableConfig panels
#

class TableConfigPanel(panels.ObjectAttributesPanel):
    title = _('Table Config')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    object_type = attrs.TextAttr('object_type')
    table = attrs.TextAttr('table')
    user = attrs.TextAttr('user')
    enabled = attrs.BooleanAttr('enabled')
    shared = attrs.BooleanAttr('shared')
    weight = attrs.NumericAttr('weight')


class TableConfigColumnsPanel(panels.ObjectPanel):
    template_name = 'extras/panels/tableconfig_columns.html'
    title = _('Columns Displayed')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'columns': context.get('columns'),
        }


class TableConfigOrderingPanel(panels.ObjectPanel):
    template_name = 'extras/panels/tableconfig_ordering.html'
    title = _('Ordering')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'columns': context.get('columns'),
        }


#
# NotificationGroup panels
#

class NotificationGroupPanel(panels.ObjectAttributesPanel):
    title = _('Notification Group')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class NotificationGroupGroupsPanel(panels.ObjectPanel):
    template_name = 'extras/panels/notificationgroup_groups.html'
    title = _('Groups')


class NotificationGroupUsersPanel(panels.ObjectPanel):
    template_name = 'extras/panels/notificationgroup_users.html'
    title = _('Users')


#
# Webhook panels
#

class WebhookPanel(panels.ObjectAttributesPanel):
    title = _('Webhook')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class WebhookHTTPPanel(panels.ObjectAttributesPanel):
    title = _('HTTP Request')

    http_method = attrs.ChoiceAttr('http_method', label=_('HTTP method'))
    payload_url = attrs.TextAttr('payload_url', label=_('Payload URL'), style='font-monospace')
    http_content_type = attrs.TextAttr('http_content_type', label=_('HTTP content type'))
    secret = attrs.TextAttr('secret')


class WebhookSSLPanel(panels.ObjectAttributesPanel):
    title = _('SSL')

    ssl_verification = attrs.BooleanAttr('ssl_verification', label=_('SSL verification'))
    ca_file_path = attrs.TextAttr('ca_file_path', label=_('CA file path'))


#
# EventRule panels
#

class EventRulePanel(panels.ObjectAttributesPanel):
    title = _('Event Rule')

    name = attrs.TextAttr('name')
    enabled = attrs.BooleanAttr('enabled')
    description = attrs.TextAttr('description')


class EventRuleEventTypesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/eventrule_event_types.html'
    title = _('Event Types')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'registry': context.get('registry'),
        }


class EventRuleActionPanel(panels.ObjectAttributesPanel):
    title = _('Action')

    action_type = attrs.ChoiceAttr('action_type', label=_('Type'))
    action_object = attrs.RelatedObjectAttr('action_object', linkify=True, label=_('Object'))
    action_data = attrs.TemplatedAttr(
        'action_data',
        label=_('Data'),
        template_name='extras/eventrule/attrs/action_data.html',
    )


#
# Tag panels
#

class TagPanel(panels.ObjectAttributesPanel):
    title = _('Tag')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    color = attrs.ColorAttr('color')
    weight = attrs.NumericAttr('weight')
    tagged_items = attrs.TemplatedAttr(
        'extras_taggeditem_items',
        template_name='extras/tag/attrs/tagged_item_count.html',
    )


class TagObjectTypesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/tag_object_types.html'
    title = _('Allowed Object Types')


class TagItemTypesPanel(panels.ObjectPanel):
    template_name = 'extras/panels/tag_item_types.html'
    title = _('Tagged Item Types')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'object_types': context.get('object_types'),
        }


#
# ConfigContextProfile panels
#

class ConfigContextProfilePanel(panels.ObjectAttributesPanel):
    title = _('Config Context Profile')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


#
# ConfigContext panels
#

class ConfigContextPanel(panels.ObjectAttributesPanel):
    title = _('Config Context')

    name = attrs.TextAttr('name')
    weight = attrs.NumericAttr('weight')
    profile = attrs.RelatedObjectAttr('profile', linkify=True)
    description = attrs.TextAttr('description')
    is_active = attrs.BooleanAttr('is_active', label=_('Active'))


class ConfigContextAssignmentPanel(panels.ObjectPanel):
    template_name = 'extras/panels/configcontext_assignment.html'
    title = _('Assignment')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'assigned_objects': context.get('assigned_objects'),
        }


#
# ConfigTemplate panels
#

class ConfigTemplatePanel(panels.ObjectAttributesPanel):
    title = _('Config Template')

    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    mime_type = attrs.TextAttr('mime_type', label=_('MIME type'))
    file_name = attrs.TextAttr('file_name')
    file_extension = attrs.TextAttr('file_extension')
    as_attachment = attrs.BooleanAttr('as_attachment', label=_('Attachment'))
    data_source = attrs.RelatedObjectAttr('data_source', linkify=True)
    data_file = attrs.TemplatedAttr(
        'data_path',
        template_name='extras/configtemplate/attrs/data_file.html',
    )
    data_synced = attrs.DateTimeAttr('data_synced')
    auto_sync_enabled = attrs.BooleanAttr('auto_sync_enabled')


#
# ImageAttachment panels
#

class ImageAttachmentPanel(panels.ObjectAttributesPanel):
    title = _('Image Attachment')

    parent = attrs.RelatedObjectAttr('parent', linkify=True, label=_('Parent object'))
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')


class ImageAttachmentFilePanel(panels.ObjectPanel):
    template_name = 'extras/panels/imageattachment_file.html'
    title = _('File')


class ImageAttachmentImagePanel(panels.ObjectPanel):
    template_name = 'extras/panels/imageattachment_image.html'
    title = _('Image')


#
# JournalEntry panels
#

class JournalEntryPanel(panels.ObjectAttributesPanel):
    title = _('Journal Entry')

    assigned_object = attrs.RelatedObjectAttr('assigned_object', linkify=True, label=_('Object'))
    created = attrs.DateTimeAttr('created', spec='minutes')
    created_by = attrs.TextAttr('created_by')
    kind = attrs.ChoiceAttr('kind')
