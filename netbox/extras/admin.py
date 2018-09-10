from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from netbox.admin import admin_site
from utilities.forms import LaxURLField
from .models import CustomField, CustomFieldChoice, Graph, ExportTemplate, TopologyMap, UserAction, Webhook


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
    payload_url = LaxURLField(
        label='URL'
    )

    class Meta:
        model = Webhook
        exclude = []

    def __init__(self, *args, **kwargs):
        super(WebhookForm, self).__init__(*args, **kwargs)

        order_content_types(self.fields['obj_type'])


@admin.register(Webhook, site=admin_site)
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


@admin.register(CustomField, site=admin_site)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceAdmin]
    list_display = ['name', 'models', 'type', 'required', 'filter_logic', 'default', 'weight', 'description']
    form = CustomFieldForm

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.obj_type.all()])


#
# Graphs
#

@admin.register(Graph, site=admin_site)
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


@admin.register(ExportTemplate, site=admin_site)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'description', 'mime_type', 'file_extension']
    form = ExportTemplateForm


#
# Topology maps
#

@admin.register(TopologyMap, site=admin_site)
class TopologyMapAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'site']
    prepopulated_fields = {
        'slug': ['name'],
    }


#
# User actions
#

@admin.register(UserAction, site=admin_site)
class UserActionAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['user', 'action', 'content_type', 'object_id', '_message']

    def _message(self, obj):
        return mark_safe(obj.message)
