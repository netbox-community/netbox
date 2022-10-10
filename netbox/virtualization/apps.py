from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from . import search
