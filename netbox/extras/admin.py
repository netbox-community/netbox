from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from utilities.forms import ContentTypeMultipleChoiceField, LaxURLField
from .models import JobResult, Webhook
from .utils import FeatureQuery


#
# Webhooks
#

class WebhookForm(forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks')
    )
    payload_url = LaxURLField(
        label='URL'
    )

    class Meta:
        model = Webhook
        exclude = ()


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'models', 'payload_url', 'http_content_type', 'enabled', 'type_create', 'type_update', 'type_delete',
        'ssl_verification',
    ]
    list_filter = [
        'enabled', 'type_create', 'type_update', 'type_delete', 'content_types',
    ]
    form = WebhookForm
    fieldsets = (
        (None, {
            'fields': ('name', 'content_types', 'enabled')
        }),
        ('Events', {
            'fields': ('type_create', 'type_update', 'type_delete')
        }),
        ('HTTP Request', {
            'fields': (
                'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
            ),
            'classes': ('monospace',)
        }),
        ('SSL', {
            'fields': ('ssl_verification', 'ca_file_path')
        })
    )

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.content_types.all()])


#
# Reports
#

@admin.register(JobResult)
class JobResultAdmin(admin.ModelAdmin):
    list_display = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status',
    ]
    fields = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status', 'data', 'job_id'
    ]
    list_filter = [
        'status',
    ]
    readonly_fields = fields

    def has_add_permission(self, request):
        return False
