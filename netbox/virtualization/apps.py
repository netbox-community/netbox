from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from . import search
        from utilities.counter import connect_counters

        connect_counters(self)
