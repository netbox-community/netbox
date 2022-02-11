from django.apps import AppConfig


class WirelessConfig(AppConfig):
    name = 'wireless'

    def ready(self):
        import wireless.signals
