from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from . import search, signals  # noqa: F401
        from .models import VirtualMachine

        # Register models
        register_models(*self.get_models())

        # Register counters
        connect_counters(VirtualMachine)
