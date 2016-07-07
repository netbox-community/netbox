from django.contrib import admin
from django.db.models import Count

from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceTemplate, Manufacturer, Module, Platform,
    PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup, Site,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'facility', 'asn']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(RackGroup)
class RackGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'site']
    prepopulated_fields = {
        'slug': ['name'],
    }


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_id', 'site', 'u_height']


#
# Device types
#

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug']


class ConsolePortTemplateAdmin(admin.TabularInline):
    model = ConsolePortTemplate


class ConsoleServerPortTemplateAdmin(admin.TabularInline):
    model = ConsoleServerPortTemplate


class PowerPortTemplateAdmin(admin.TabularInline):
    model = PowerPortTemplate


class PowerOutletTemplateAdmin(admin.TabularInline):
    model = PowerOutletTemplate


class InterfaceTemplateAdmin(admin.TabularInline):
    model = InterfaceTemplate


class DeviceBayTemplateAdmin(admin.TabularInline):
    model = DeviceBayTemplate


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['model'],
    }
    inlines = [
        ConsolePortTemplateAdmin,
        ConsoleServerPortTemplateAdmin,
        PowerPortTemplateAdmin,
        PowerOutletTemplateAdmin,
        InterfaceTemplateAdmin,
        DeviceBayTemplateAdmin,
    ]
    list_display = ['model', 'manufacturer', 'slug', 'u_height', 'console_ports', 'console_server_ports', 'power_ports',
                    'power_outlets', 'interfaces', 'device_bays']
    list_filter = ['manufacturer']

    def get_queryset(self, request):
        return DeviceType.objects.annotate(
            console_port_count=Count('console_port_templates', distinct=True),
            cs_port_count=Count('cs_port_templates', distinct=True),
            power_port_count=Count('power_port_templates', distinct=True),
            power_outlet_count=Count('power_outlet_templates', distinct=True),
            interface_count=Count('interface_templates', distinct=True),
            devicebay_count=Count('devicebay_templates', distinct=True),
        )

    def console_ports(self, instance):
        return instance.console_port_count

    def console_server_ports(self, instance):
        return instance.cs_port_count

    def power_ports(self, instance):
        return instance.power_port_count

    def power_outlets(self, instance):
        return instance.power_outlet_count

    def interfaces(self, instance):
        return instance.interface_count

    def device_bays(self, instance):
        return instance.devicebay_count


#
# Devices
#

@admin.register(DeviceRole)
class DeviceRoleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'slug', 'color']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['name'],
    }
    list_display = ['name', 'rpc_client']


class ConsolePortAdmin(admin.TabularInline):
    model = ConsolePort
    readonly_fields = ['cs_port']


class ConsoleServerPortAdmin(admin.TabularInline):
    model = ConsoleServerPort


class PowerPortAdmin(admin.TabularInline):
    model = PowerPort
    readonly_fields = ['power_outlet']


class PowerOutletAdmin(admin.TabularInline):
    model = PowerOutlet


class InterfaceAdmin(admin.TabularInline):
    model = Interface


class DeviceBayAdmin(admin.TabularInline):
    model = DeviceBay
    fk_name = 'device'
    readonly_fields = ['installed_device']


class ModuleAdmin(admin.TabularInline):
    model = Module
    readonly_fields = ['parent', 'discovered']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        ConsolePortAdmin,
        ConsoleServerPortAdmin,
        PowerPortAdmin,
        PowerOutletAdmin,
        InterfaceAdmin,
        DeviceBayAdmin,
        ModuleAdmin,
    ]
    list_display = ['display_name', 'device_type', 'device_role', 'primary_ip', 'rack', 'position', 'serial']
    list_filter = ['device_role']

    def get_queryset(self, request):
        qs = super(DeviceAdmin, self).get_queryset(request)
        return qs.select_related('device_type__manufacturer', 'device_role', 'primary_ip', 'rack')
