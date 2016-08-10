from django.contrib import admin

from .models import Provider, CircuitType, Circuit


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug', 'asn']


@admin.register(CircuitType)
class CircuitTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug']


@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ['cid', 'provider', 'type', 'tenant', 'site', 'install_date', 'port_speed_human',
                    'upstream_speed_human', 'commit_rate_human', 'xconnect_id']
    list_filter = ['provider', 'type', 'tenant']
    exclude = ['interface']

    def get_queryset(self, request):
        qs = super(CircuitAdmin, self).get_queryset(request)
        return qs.select_related('provider', 'type', 'tenant', 'site')
