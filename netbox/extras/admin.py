from django import forms
from django.contrib import admin

from .models import CustomField, CustomFieldChoice, Graph, ExportTemplate, TopologyMap, UserAction


class CustomFieldForm(forms.ModelForm):

    class Meta:
        model = CustomField
        exclude = []

    def __init__(self, *args, **kwargs):
        super(CustomFieldForm, self).__init__(*args, **kwargs)

        # Organize the available ContentTypes
        queryset = self.fields['obj_type'].queryset.order_by('app_label', 'model')
        self.fields['obj_type'].choices = [(ct.pk, '{} > {}'.format(ct.app_label, ct.name)) for ct in queryset]


class CustomFieldChoiceAdmin(admin.TabularInline):
    model = CustomFieldChoice
    extra = 5


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceAdmin]
    list_display = ['name', 'models', 'type', 'required', 'default', 'weight', 'description']
    form = CustomFieldForm

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.obj_type.all()])


@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'weight', 'source']


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'name', 'mime_type', 'file_extension']


@admin.register(TopologyMap)
class TopologyMapAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'site']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['user', 'action', 'content_type', 'object_id', 'message']
