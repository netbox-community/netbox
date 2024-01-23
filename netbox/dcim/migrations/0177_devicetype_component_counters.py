from django.db import migrations
from django.db.models import Count

import utilities.fields
from utilities.counters import update_counts


def recalculate_devicetype_template_counts(apps, schema_editor):
    DeviceType = apps.get_model("dcim", "DeviceType")

    update_counts(DeviceType, 'console_port_template_count', 'consoleporttemplates')
    update_counts(DeviceType, 'console_server_port_template_count', 'consoleserverporttemplates')
    update_counts(DeviceType, 'power_port_template_count', 'powerporttemplates')
    update_counts(DeviceType, 'power_outlet_template_count', 'poweroutlettemplates')
    update_counts(DeviceType, 'interface_template_count', 'interfacetemplates')
    update_counts(DeviceType, 'front_port_template_count', 'frontporttemplates')
    update_counts(DeviceType, 'rear_port_template_count', 'rearporttemplates')
    update_counts(DeviceType, 'device_bay_template_count', 'devicebaytemplates')
    update_counts(DeviceType, 'module_bay_template_count', 'modulebaytemplates')
    update_counts(DeviceType, 'inventory_item_template_count', 'inventoryitemtemplates')


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
