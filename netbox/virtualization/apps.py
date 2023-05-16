from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from . import search
        from .models import VMInterface

        from utilities.counter import connect_counter

        connect_counter('_interface_count', VMInterface.virtual_machine)
