from django.db import migrations
from django.db.models import Count

import utilities.fields


def recalculate_devicetype_template_counts(apps, schema_editor):
    DeviceType = apps.get_model("dcim", "DeviceType")
    device_types = list(DeviceType.objects.all().annotate(
        _console_port_template_count=Count('consoleporttemplates', distinct=True),
        _console_server_port_template_count=Count('consoleserverporttemplates', distinct=True),
        _power_port_template_count=Count('powerporttemplates', distinct=True),
        _power_outlet_template_count=Count('poweroutlettemplates', distinct=True),
        _interface_template_count=Count('interfacetemplates', distinct=True),
        _front_port_template_count=Count('frontporttemplates', distinct=True),
        _rear_port_template_count=Count('rearporttemplates', distinct=True),
        _device_bay_template_count=Count('devicebaytemplates', distinct=True),
        _module_bay_template_count=Count('modulebaytemplates', distinct=True),
        _inventory_item_template_count=Count('inventoryitemtemplates', distinct=True),
    ))

    for devicetype in device_types:
        devicetype.console_port_template_count = devicetype._console_port_template_count
        devicetype.console_server_port_template_count = devicetype._console_server_port_template_count
        devicetype.power_port_template_count = devicetype._power_port_template_count
        devicetype.power_outlet_template_count = devicetype._power_outlet_template_count
        devicetype.interface_template_count = devicetype._interface_template_count
        devicetype.front_port_template_count = devicetype._front_port_template_count
        devicetype.rear_port_template_count = devicetype._rear_port_template_count
        devicetype.device_bay_template_count = devicetype._device_bay_template_count
        devicetype.module_bay_template_count = devicetype._module_bay_template_count
        devicetype.inventory_item_template_count = devicetype._inventory_item_template_count

    DeviceType.objects.bulk_update(device_types, [
        'console_port_template_count',
        'console_server_port_template_count',
        'power_port_template_count',
        'power_outlet_template_count',
        'interface_template_count',
        'front_port_template_count',
        'rear_port_template_count',
        'device_bay_template_count',
        'module_bay_template_count',
        'inventory_item_template_count',
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0176_device_component_counters'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='console_port_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.ConsolePortTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='console_server_port_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.ConsoleServerPortTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='power_port_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.PowerPortTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='power_outlet_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.PowerOutletTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='interface_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.InterfaceTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='front_port_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.FrontPortTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='rear_port_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.RearPortTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='device_bay_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.DeviceBayTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='module_bay_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.ModuleBayTemplate'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='inventory_item_template_count',
            field=utilities.fields.CounterCacheField(default=0, to_field='device_type', to_model='dcim.InventoryItemTemplate'),
        ),
        migrations.RunPython(
            recalculate_devicetype_template_counts,
            reverse_code=migrations.RunPython.noop
        ),
    ]
