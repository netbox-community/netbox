from django.contrib import admin

from .models import Tenant, TenantGroup


@admin.register(TenantGroup)
class TenantGroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug', 'group']

    def get_queryset(self, request):
        qs = super(TenantAdmin, self).get_queryset(request)
        return qs.select_related('group')
