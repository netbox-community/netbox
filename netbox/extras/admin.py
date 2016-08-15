from django.contrib import admin

from .models import CustomField, CustomFieldValue, CustomFieldChoice, Graph, ExportTemplate, TopologyMap, UserAction


class CustomFieldChoiceAdmin(admin.TabularInline):
    model = CustomFieldChoice


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceAdmin]
    list_display = ['name', 'models', 'type', 'required', 'default', 'description']

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
