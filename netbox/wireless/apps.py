from django.apps import AppConfig


class WirelessConfig(AppConfig):
    name = 'wireless'

    def ready(self):
        from netbox.models.features import register_model
        from . import signals, search

        # Register models
        for model in self.get_models():
            register_model(model)
