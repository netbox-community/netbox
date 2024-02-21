from django.apps import AppConfig


class VPNConfig(AppConfig):
    name = 'vpn'
    verbose_name = 'VPN'

    def ready(self):
        from netbox.models.features import register_models
        from . import search

        # Register models
        register_models(*self.get_models())
