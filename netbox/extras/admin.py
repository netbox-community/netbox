from django import forms
from django.contrib import admin

from utilities.forms import LaxURLField
from .choices import CustomFieldTypeChoices
from .models import CustomField, CustomLink, ExportTemplate, JobResult, Webhook


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
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'obj_type' in self.fields:
            order_content_types(self.fields['obj_type'])


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'models', 'payload_url', 'http_content_type', 'enabled', 'type_create', 'type_update', 'type_delete',
        'ssl_verification',
    ]
    list_filter = [
        'enabled', 'type_create', 'type_update', 'type_delete', 'obj_type',
    ]
    form = WebhookForm
    fieldsets = (
        (None, {
            'fields': ('name', 'obj_type', 'enabled')
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
        return ', '.join([ct.name for ct in obj.obj_type.all()])


#
# Custom fields
#

class CustomFieldForm(forms.ModelForm):

    class Meta:
        model = CustomField
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        order_content_types(self.fields['content_types'])

    def clean(self):

        # Validate selection choices
        if self.cleaned_data['type'] == CustomFieldTypeChoices.TYPE_SELECT and len(self.cleaned_data['choices']) < 2:
            raise forms.ValidationError({
                'choices': 'Selection fields must specify at least two choices.'
            })


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    actions = None
    form = CustomFieldForm
    list_display = [
        'name', 'models', 'type', 'required', 'filter_logic', 'default', 'weight', 'description',
    ]
    list_filter = [
        'type', 'required', 'content_types',
    ]
    fieldsets = (
        ('Custom Field', {
            'fields': ('type', 'name', 'weight', 'label', 'description', 'required', 'default', 'filter_logic')
        }),
        ('Assignment', {
            'description': 'A custom field must be assigned to one or more object types.',
            'fields': ('content_types',)
        }),
        ('Validation Rules', {
            'fields': ('validation_minimum', 'validation_maximum', 'validation_regex')
        }),
        ('Choices', {
            'description': 'A selection field must have two or more choices assigned to it.',
            'fields': ('choices',)
        })
    )

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.content_types.all()])


#
# Custom links
#

class CustomLinkForm(forms.ModelForm):

    class Meta:
        model = CustomLink
        exclude = []
        widgets = {
            'text': forms.Textarea,
            'url': forms.Textarea,
        }
        help_texts = {
            'weight': 'A numeric weight to influence the ordering of this link among its peers. Lower weights appear '
                      'first in a list.',
            'text': 'Jinja2 template code for the link text. Reference the object as <code>{{ obj }}</code>. Links '
                    'which render as empty text will not be displayed.',
            'url': 'Jinja2 template code for the link URL. Reference the object as <code>{{ obj }}</code>.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_type'])
        self.fields['content_type'].choices.insert(0, ('', '---------'))


@admin.register(CustomLink)
class CustomLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Custom Link', {
            'fields': ('content_type', 'name', 'group_name', 'weight', 'button_class', 'new_window')
        }),
        ('Templates', {
            'fields': ('text', 'url'),
            'classes': ('monospace',)
        })
    )
    list_display = [
        'name', 'content_type', 'group_name', 'weight',
    ]
    list_filter = [
        'content_type',
    ]
    form = CustomLinkForm


#
# Export templates
#

class ExportTemplateForm(forms.ModelForm):

    class Meta:
        model = ExportTemplate
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_type'])
        self.fields['content_type'].choices.insert(0, ('', '---------'))


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Export Template', {
            'fields': ('content_type', 'name', 'description', 'mime_type', 'file_extension')
        }),
        ('Content', {
            'fields': ('template_code',),
            'classes': ('monospace',)
        })
    )
    list_display = [
        'name', 'content_type', 'description', 'mime_type', 'file_extension',
    ]
    list_filter = [
        'content_type',
    ]
    form = ExportTemplateForm


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
