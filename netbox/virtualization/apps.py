from django.apps import AppConfig

from netbox import denormalized


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from . import search, signals
        from .models import VirtualMachine

        # Register models
        register_models(*self.get_models())

        # Register denormalized fields
        denormalized.register(VirtualMachine, 'cluster', {
            'site': 'site',
        })

        # Register counters
        connect_counters(VirtualMachine)
