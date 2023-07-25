from django.db import migrations
from django.db.models import Count

import utilities.fields


def recalculate_device_counts(apps, schema_editor):
    Device = apps.get_model("dcim", "Device")
    devices = list(Device.objects.all().annotate(
        _console_port_count=Count('consoleports', distinct=True),
        _console_server_port_count=Count('consoleserverports', distinct=True),
        _power_port_count=Count('powerports', distinct=True),
        _power_outlet_count=Count('poweroutlets', distinct=True),
        _interface_count=Count('interfaces', distinct=True),
        _front_port_count=Count('frontports', distinct=True),
        _rear_port_count=Count('rearports', distinct=True),
        _device_bay_count=Count('devicebays', distinct=True),
        _module_bay_count=Count('modulebays', distinct=True),
        _inventory_item_count=Count('inventoryitems', distinct=True),
    ))

    for device in devices:
        device.console_port_count = device._console_port_count
        device.console_server_port_count = device._console_server_port_count
        device.power_port_count = device._power_port_count
        device.power_outlet_count = device._power_outlet_count
        device.interface_count = device._interface_count
        device.front_port_count = device._front_port_count
        device.rear_port_count = device._rear_port_count
        device.device_bay_count = device._device_bay_count
        device.module_bay_count = device._module_bay_count
        device.inventory_item_count = device._inventory_item_count

    Device.objects.bulk_update(devices, [
        'console_port_count', 'console_server_port_count', 'power_port_count', 'power_outlet_count', 'interface_count',
        'front_port_count', 'rear_port_count', 'device_bay_count', 'module_bay_count', 'inventory_item_count',
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0174_rack_starting_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='console_port_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.ConsolePort'),
        ),
        migrations.AddField(
            model_name='device',
            name='console_server_port_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.ConsoleServerPort'),
        ),
        migrations.AddField(
            model_name='device',
            name='power_port_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.PowerPort'),
        ),
        migrations.AddField(
            model_name='device',
            name='power_outlet_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.PowerOutlet'),
        ),
        migrations.AddField(
            model_name='device',
            name='interface_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.Interface'),
        ),
        migrations.AddField(
            model_name='device',
            name='front_port_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.FrontPort'),
        ),
        migrations.AddField(
            model_name='device',
            name='rear_port_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.RearPort'),
        ),
        migrations.AddField(
            model_name='device',
            name='device_bay_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.DeviceBay'),
        ),
        migrations.AddField(
            model_name='device',
            name='module_bay_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.ModuleBay'),
        ),
        migrations.AddField(
            model_name='device',
            name='inventory_item_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device', to_model='dcim.InventoryItem'),
        ),
        migrations.RunPython(
            recalculate_device_counts,
            reverse_code=migrations.RunPython.noop
        ),
    ]
