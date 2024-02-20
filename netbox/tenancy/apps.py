from django.apps import AppConfig


class TenancyConfig(AppConfig):
    name = 'tenancy'

    def ready(self):
        from netbox.models.features import register_model
        from . import search

        # Register models
        for model in self.get_models():
            register_model(model)
