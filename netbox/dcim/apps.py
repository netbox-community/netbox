from django.apps import AppConfig


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from netbox.models.features import register_models
        from utilities.counters import connect_counters

        from . import search, signals  # noqa: F401
        from .models import Device, DeviceType, ModuleType, RackType, VirtualChassis
        from .ui import breadcrumbs  # noqa: F401

        # Register models
        register_models(*self.get_models())

        # Register counters
        connect_counters(Device, DeviceType, ModuleType, RackType, VirtualChassis)
