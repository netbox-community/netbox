from django.apps import AppConfig

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

        from utilities.counter import connect_counter

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

        connect_counter('_console_port_count', ConsolePort.device)
        connect_counter('_console_server_port_count', ConsoleServerPort.device)
        connect_counter('_interface_count', Interface.device)
        connect_counter('_front_port_count', FrontPort.device)
        connect_counter('_rear_port_count', RearPort.device)
        connect_counter('_device_bay_count', DeviceBay.device)
        connect_counter('_inventory_item_count', InventoryItem.device)
        connect_counter('_power_port_count', PowerPort.device)
        connect_counter('_power_outlet_count', PowerOutlet.device)
