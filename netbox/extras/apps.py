from django.apps import AppConfig


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        from netbox.models.features import register_models
        from . import dashboard, lookups, search, signals  # noqa: F401

        # Register models
        register_models(*self.get_models())
