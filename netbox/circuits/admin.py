from django.contrib import admin

from .models import Provider, CircuitType, Circuit, Termination


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
    list_display = ['cid', 'provider', 'type', 'tenant', 'install_date']
    list_filter = ['provider', 'type', 'tenant']

    def get_queryset(self, request):
        qs = super(CircuitAdmin, self).get_queryset(request)
        return qs.select_related('provider', 'type', 'tenant')


@admin.register(Termination)
class TerminationAdmin(admin.ModelAdmin):
    list_display = ['tid', 'circuit', 'site', 'port_speed_human',
                    'upstream_speed_human', 'commit_rate_human', 'xconnect_id']
    list_filter = ['site', 'tid', 'circuit']
    exclude = ['interface']

    def get_queryset(self, request):
        qs = super(TerminationAdmin, self).get_queryset(request)
        return qs.select_related('site', 'circuit')
