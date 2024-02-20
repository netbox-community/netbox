from django.apps import AppConfig


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        from netbox.models.features import register_model
        from . import dashboard, lookups, search, signals

        # Register models
        for model in self.get_models():
            register_model(model)
