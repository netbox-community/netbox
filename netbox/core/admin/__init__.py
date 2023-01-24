from django.contrib import admin

from core.models import DataFile, DataSource


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_count')

    @staticmethod
    def file_count(obj):
        return obj.datafiles.count()


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = ('path', 'size')
    readonly_fields = ('source', 'path', 'last_updated', 'size', 'checksum')
