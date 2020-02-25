from django import forms
from django.contrib import admin

from netbox.admin import admin_site
from utilities.forms import LaxURLField
from .models import CustomField, CustomFieldChoice, CustomLink, Graph, ExportTemplate, ReportResult, Webhook
from .reports import get_report


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


@admin.register(Webhook, site=admin_site)
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
            'fields': (
                'name', 'obj_type', 'enabled',
            )
        }),
        ('Events', {
            'fields': (
                'type_create', 'type_update', 'type_delete',
            )
        }),
        ('HTTP Request', {
            'fields': (
                'http_method', 'payload_url', 'http_content_type', 'additional_headers', 'body_template', 'secret',
            )
        }),
        ('SSL', {
            'fields': (
                'ssl_verification', 'ca_file_path',
            )
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


@admin.register(CustomField, site=admin_site)
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
            'text': 'Jinja2 template code for the link text. Reference the object as <code>{{ obj }}</code>. Links '
                    'which render as empty text will not be displayed.',
            'url': 'Jinja2 template code for the link URL. Reference the object as <code>{{ obj }}</code>.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_type'])
        self.fields['content_type'].choices.insert(0, ('', '---------'))


@admin.register(CustomLink, site=admin_site)
class CustomLinkAdmin(admin.ModelAdmin):
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

@admin.register(Graph, site=admin_site)
class GraphAdmin(admin.ModelAdmin):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_type'])
        self.fields['content_type'].choices.insert(0, ('', '---------'))


@admin.register(ExportTemplate, site=admin_site)
class ExportTemplateAdmin(admin.ModelAdmin):
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

@admin.register(ReportResult, site=admin_site)
class ReportResultAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'active', 'created', 'user', 'passing',
    ]
    fields = [
        'report', 'user', 'passing', 'data',
    ]
    list_filter = [
        'failed',
    ]
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def active(self, obj):
        module, report_name = obj.report.split('.')
        return True if get_report(module, report_name) else False
    active.boolean = True

    def passing(self, obj):
        return not obj.failed
    passing.boolean = True
