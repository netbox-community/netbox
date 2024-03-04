from django.apps import AppConfig


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = "Circuits"

    def ready(self):
        from netbox.models.features import register_models
        from . import signals, search

        # Register models
        register_models(*self.get_models())
