from django.apps import AppConfig, apps

from netbox import denormalized


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):
        from . import signals, search
        from .models import (
            CableTermination, ConsolePort, ConsoleServerPort, DeviceBay, FrontPort,
            Interface, InventoryItem, PowerOutlet, PowerPort, RearPort,
        )

        from utilities.counter import connect_counters

        # Register denormalized fields
        denormalized.register(CableTermination, '_device', {
            '_rack': 'rack',
            '_location': 'location',
            '_site': 'site',
        })
        denormalized.register(CableTermination, '_rack', {
            '_location': 'location',
            '_site': 'site',
        })
        denormalized.register(CableTermination, '_location', {
            '_site': 'site',
        })

        connect_counters(self)
