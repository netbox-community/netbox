from django.apps import AppConfig

from netbox import denormalized


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from . import signals, search
        from .models import CableTermination, Device, DeviceType, VirtualChassis

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

        # Register counters
        connect_counters(Device, DeviceType, VirtualChassis)
