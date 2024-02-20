from django.apps import AppConfig


class VPNConfig(AppConfig):
    name = 'vpn'
    verbose_name = 'VPN'

    def ready(self):
        from netbox.models.features import register_model
        from . import search

        # Register models
        for model in self.get_models():
            register_model(model)
