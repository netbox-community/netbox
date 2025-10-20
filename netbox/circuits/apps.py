from django.apps import AppConfig

from netbox import denormalized


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = "Circuits"

    def ready(self):
        from netbox.models.features import register_models
        from . import signals, search  # noqa: F401
        from .models import CircuitTermination

        # Register models
        register_models(*self.get_models())

        denormalized.register(CircuitTermination, '_site', {
            '_region': 'region',
            '_site_group': 'group',
        })

        denormalized.register(CircuitTermination, '_location', {
            '_site': 'site',
        })
