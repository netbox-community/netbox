from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from utilities.forms import LaxURLField
from .constants import OBJECTCHANGE_ACTION_CREATE, OBJECTCHANGE_ACTION_DELETE, OBJECTCHANGE_ACTION_UPDATE
from .models import (
    ConfigContext, CustomField, CustomFieldChoice, Graph, ExportTemplate, ObjectChange, TopologyMap, UserAction,
    Webhook,
)


def order_content_types(field):
    """
    Order the list of available ContentTypes by application
    """
    queryset = field.queryset.order_by('app_label', 'model')
    field.choices = [(ct.pk, '{} > {}'.format(ct.app_label, ct.name)) for ct in queryset]


#
# Webhooks
#

class WebhookForm(forms.ModelForm):

    payload_url = LaxURLField()

    class Meta:
        model = Webhook
        exclude = []

    def __init__(self, *args, **kwargs):
        super(WebhookForm, self).__init__(*args, **kwargs)

        order_content_types(self.fields['obj_type'])


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'models', 'payload_url', 'http_content_type', 'enabled', 'type_create', 'type_update',
        'type_delete', 'ssl_verification',
    ]
    form = WebhookForm

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.obj_type.all()])


#
# Custom fields
#

class CustomFieldForm(forms.ModelForm):

    class Meta:
        model = CustomField
        exclude = []

    def __init__(self, *args, **kwargs):
        super(CustomFieldForm, self).__init__(*args, **kwargs)

        order_content_types(self.fields['obj_type'])


class CustomFieldChoiceAdmin(admin.TabularInline):
    model = CustomFieldChoice
    extra = 5


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceAdmin]
    list_display = ['name', 'models', 'type', 'required', 'filter_logic', 'default', 'weight', 'description']
    form = CustomFieldForm

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.obj_type.all()])


#
# Graphs
#

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'weight', 'source']


#
# Export templates
#

class ExportTemplateForm(forms.ModelForm):

    class Meta:
        model = ExportTemplate
        exclude = []

    def __init__(self, *args, **kwargs):
        super(ExportTemplateForm, self).__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_type'])
        self.fields['content_type'].choices.insert(0, ('', '---------'))


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'description', 'mime_type', 'file_extension']
    form = ExportTemplateForm


#
# Topology maps
#

@admin.register(TopologyMap)
class TopologyMapAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'site']
    prepopulated_fields = {
        'slug': ['name'],
    }


#
# Config contexts
#

@admin.register(ConfigContext)
class ConfigContextAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight']


#
# Change logging
#

@admin.register(ObjectChange)
class ObjectChangeAdmin(admin.ModelAdmin):
    actions = None
    fields = ['time', 'changed_object_type', 'display_object', 'action', 'display_user', 'request_id', 'object_data']
    list_display = ['time', 'changed_object_type', 'display_object', 'display_action', 'display_user', 'request_id']
    list_filter = ['time', 'action', 'user__username']
    list_select_related = ['changed_object_type', 'user']
    readonly_fields = fields
    search_fields = ['user_name', 'object_repr', 'request_id']

    def has_add_permission(self, request):
        return False

    def display_user(self, obj):
        if obj.user is not None:
            return obj.user
        else:
            return '{} (deleted)'.format(obj.user_name)
    display_user.short_description = 'user'

    def display_action(self, obj):
        icon = {
            OBJECTCHANGE_ACTION_CREATE: 'addlink',
            OBJECTCHANGE_ACTION_UPDATE: 'changelink',
            OBJECTCHANGE_ACTION_DELETE: 'deletelink',
        }
        return mark_safe('<span class="{}">{}</span>'.format(icon[obj.action], obj.get_action_display()))
    display_action.short_description = 'action'

    def display_object(self, obj):
        if hasattr(obj.changed_object, 'get_absolute_url'):
            return mark_safe('<a href="{}">{}</a>'.format(obj.changed_object.get_absolute_url(), obj.changed_object))
        elif obj.changed_object is not None:
            return obj.changed_object
        else:
            return '{} (deleted)'.format(obj.object_repr)
    display_object.short_description = 'object'


#
# User actions
#

@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['user', 'action', 'content_type', 'object_id', '_message']

    def _message(self, obj):
        return mark_safe(obj.message)
