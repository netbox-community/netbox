from django.contrib import admin

from .models import (
    Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VLANGroup, VRF,
)


@admin.register(VRF)
class VRFAdmin(admin.ModelAdmin):
    list_display = ['name', 'rd']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug', 'weight']


@admin.register(RIR)
class RIRAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug']


@admin.register(Aggregate)
class AggregateAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'rir', 'date_added']
    list_filter = ['family', 'rir']
    search_fields = ['prefix']


@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'vrf', 'site', 'status', 'role', 'vlan']
    list_filter = ['family', 'site', 'status', 'role']
    search_fields = ['prefix']

    def get_queryset(self, request):
        qs = super(PrefixAdmin, self).get_queryset(request)
        return qs.select_related('vrf', 'site', 'role', 'vlan')


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'vrf', 'nat_inside']
    list_filter = ['family']
    fields = ['address', 'vrf', 'device', 'interface', 'nat_inside']
    readonly_fields = ['interface', 'device', 'nat_inside']
    search_fields = ['address']

    def get_queryset(self, request):
        qs = super(IPAddressAdmin, self).get_queryset(request)
        return qs.select_related('vrf', 'nat_inside')


@admin.register(VLANGroup)
class VLANGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'slug']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(VLAN)
class VLANAdmin(admin.ModelAdmin):
    list_display = ['site', 'vid', 'name', 'status', 'role']
    list_filter = ['site', 'status', 'role']
    search_fields = ['vid', 'name']

    def get_queryset(self, request):
        qs = super(VLANAdmin, self).get_queryset(request)
        return qs.select_related('site', 'role')
