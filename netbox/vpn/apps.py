from django.apps import AppConfig


class VPNConfig(AppConfig):
    name = 'vpn'
    verbose_name = 'VPN'

    def ready(self):
        from . import search
