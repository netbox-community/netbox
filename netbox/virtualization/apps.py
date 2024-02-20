from django.apps import AppConfig

from netbox import denormalized


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from netbox.models.features import register_model
        from utilities.counters import connect_counters
        from . import search, signals
        from .models import VirtualMachine

        # Register models
        for model in self.get_models():
            register_model(model)

        # Register denormalized fields
        denormalized.register(VirtualMachine, 'cluster', {
            'site': 'site',
        })

        # Register counters
        connect_counters(VirtualMachine)
