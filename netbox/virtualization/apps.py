from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from netbox.models.features import register_models

        from . import denorm, search, side_effects, signals, validators  # noqa: F401

        # Register models
        register_models(*self.get_models())
