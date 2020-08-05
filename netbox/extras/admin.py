from django import forms
from django.contrib import admin

from utilities.forms import LaxURLField
from .models import CustomField, CustomFieldChoice, CustomLink, Graph, ExportTemplate, JobResult, Webhook


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

        order_content_types(self.fields['obj_type'])


class CustomFieldChoiceAdmin(admin.TabularInline):
    model = CustomFieldChoice
    extra = 5


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceAdmin]
    list_display = [
        'name', 'models', 'type', 'required', 'filter_logic', 'default', 'weight', 'description',
    ]
    list_filter = [
        'type', 'required', 'obj_type',
    ]
    form = CustomFieldForm

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.obj_type.all()])


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
# Graphs
#

class GraphForm(forms.ModelForm):

    class Meta:
        model = Graph
        exclude = ()
        help_texts = {
            'template_language': "<a href=\"https://jinja.palletsprojects.com\">Jinja2</a> is strongly recommended for "
                                 "new graphs."
        }
        widgets = {
            'source': forms.Textarea,
            'link': forms.Textarea,
        }


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Graph', {
            'fields': ('type', 'name', 'weight')
        }),
        ('Templates', {
            'fields': ('template_language', 'source', 'link'),
            'classes': ('monospace',)
        })
    )
    form = GraphForm
    list_display = [
        'name', 'type', 'weight', 'template_language', 'source',
    ]
    list_filter = [
        'type', 'template_language',
    ]


#
# Export templates
#

class ExportTemplateForm(forms.ModelForm):

    class Meta:
        model = ExportTemplate
        exclude = []
        help_texts = {
            'template_language': "<strong>Warning:</strong> Support for Django templating will be dropped in NetBox "
                                 "v2.10. <a href=\"https://jinja.palletsprojects.com\">Jinja2</a> is strongly "
                                 "recommended."
        }

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
            'fields': ('template_language', 'template_code'),
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
