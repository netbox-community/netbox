from django.apps import AppConfig

from netbox import denormalized


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from django.utils.translation import gettext as _

        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from utilities.permissions import ModelAction, register_model_actions

        from . import search, signals  # noqa: F401
        from .models import CableTermination, Device, DeviceType, ModuleType, RackType, VirtualChassis

        # Register models
        register_models(*self.get_models())

        # Register custom permission actions
        register_model_actions(Device, [
            ModelAction('render_config', help_text=_('Render device configuration')),
        ])

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
        connect_counters(Device, DeviceType, ModuleType, RackType, VirtualChassis)
