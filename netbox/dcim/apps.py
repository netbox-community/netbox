from django.apps import AppConfig

from netbox import denormalized


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from . import signals, search  # noqa: F401
        from .models import CableTermination, Device, DeviceType, ModuleType, RackType, VirtualChassis

        # Register models
        register_models(*self.get_models())

        # Register denormalized fields
        denormalized.register(CableTermination, '_device', {
            '_rack': 'rack',
            '_location': 'location',
            '_site': 'site',
        })
        denormalized.register(CableTermination, '_rack', {
            '_location': 'location',
            '_site': 'site',
        })
        denormalized.register(CableTermination, '_location', {
            '_site': 'site',
        })
        denormalized.register(Device, 'virtual_chassis', {
            '_virtual_chassis_name': 'name',
        })
        denormalized.register(Device, 'primary_ip4', {
            '_primary_ip4_address': 'address',
        })
        denormalized.register(Device, 'primary_ip6', {
            '_primary_ip6_address': 'address',
        })

        # Register counters
        connect_counters(Device, DeviceType, ModuleType, RackType, VirtualChassis)
