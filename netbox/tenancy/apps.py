from django.apps import AppConfig


class TenancyConfig(AppConfig):
    name = 'tenancy'

    def ready(self):
        from netbox.models.features import register_models
        from . import search

        # Register models
        register_models(*self.get_models())
