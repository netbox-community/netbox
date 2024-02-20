from django.apps import AppConfig

from netbox import denormalized


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from netbox.models.features import register_model
        from utilities.counters import connect_counters
        from . import signals, search
        from .models import CableTermination, Device, DeviceType, VirtualChassis

        # Register models
        for model in self.get_models():
            register_model(model)

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
