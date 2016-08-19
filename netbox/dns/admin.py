from django.contrib import admin

from .models import (
    Zone, Record,
)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'ttl', 'soa_name', 'soa_contact', 'soa_serial']
    prepopulated_fields = {
        'soa_name': ['name'],
    }


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'record_type', 'priority', 'address', 'value']
