from django.db import migrations
from django.db.models import Count

import utilities.fields
from utilities.counters import update_counts


def recalculate_device_counts(apps, schema_editor):
    Device = apps.get_model("dcim", "Device")

    update_counts(Device, 'console_port_count', 'consoleports')
    update_counts(Device, 'console_server_port_count', 'consoleserverports')
    update_counts(Device, 'power_port_count', 'powerports')
    update_counts(Device, 'power_outlet_count', 'poweroutlets')
    update_counts(Device, 'interface_count', 'interfaces')
    update_counts(Device, 'front_port_count', 'frontports')
    update_counts(Device, 'rear_port_count', 'rearports')
    update_counts(Device, 'device_bay_count', 'devicebays')
    update_counts(Device, 'module_bay_count', 'modulebays')
    update_counts(Device, 'inventory_item_count', 'inventoryitems')


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0175_device_oob_ip'),
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
