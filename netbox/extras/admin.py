from django.contrib import admin

from .models import Graph, ExportTemplate, TopologyMap, UserAction


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
