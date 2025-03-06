import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import utilities.fields


class Migration(migrations.Migration):
    replaces = [
        ('dcim', '0167_module_status'),
        ('dcim', '0168_interface_template_enabled'),
        ('dcim', '0169_devicetype_default_platform'),
        ('dcim', '0170_configtemplate'),
        ('dcim', '0171_cabletermination_change_logging'),
        ('dcim', '0172_larger_power_draw_values'),
        ('dcim', '0173_remove_napalm_fields'),
        ('dcim', '0174_device_latitude_device_longitude'),
        ('dcim', '0174_rack_starting_unit'),
        ('dcim', '0175_device_oob_ip'),
        ('dcim', '0176_device_component_counters'),
        ('dcim', '0177_devicetype_component_counters'),
        ('dcim', '0178_virtual_chassis_member_counter'),
        ('dcim', '0179_interfacetemplate_rf_role'),
        ('dcim', '0180_powerfeed_tenant'),
        ('dcim', '0181_rename_device_role_device_role'),
        ('dcim', '0182_zero_length_cable_fix'),
    ]

    dependencies = [
        ('extras', '0086_configtemplate'),
        ('tenancy', '0010_tenant_relax_uniqueness'),
        ('ipam', '0047_squashed_0053'),
        ('dcim', '0166_virtualdevicecontext'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='bridge',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bridge_interfaces',
                to='dcim.interfacetemplate',
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='default_platform',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.platform',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='config_template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='%(class)ss',
                to='extras.configtemplate',
            ),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='config_template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='device_roles',
                to='extras.configtemplate',
            ),
        ),
        migrations.AddField(
            model_name='platform',
            name='config_template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='platforms',
                to='extras.configtemplate',
            ),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='allocated_draw',
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='maximum_draw',
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='allocated_draw',
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='maximum_draw',
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.RemoveField(
            model_name='platform',
            name='napalm_args',
        ),
        migrations.RemoveField(
            model_name='platform',
            name='napalm_driver',
        ),
        migrations.AddField(
            model_name='device',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='starting_unit',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='device',
            name='oob_ip',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='ipam.ipaddress',
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='console_port_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.ConsolePort'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='console_server_port_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.ConsoleServerPort'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='power_port_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.PowerPort'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='power_outlet_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.PowerOutlet'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='interface_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.Interface'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='front_port_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.FrontPort'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='rear_port_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.RearPort'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='device_bay_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.DeviceBay'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='module_bay_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.ModuleBay'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='inventory_item_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device', to_model='dcim.InventoryItem'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='console_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.ConsolePortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='console_server_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.ConsoleServerPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='power_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.PowerPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='power_outlet_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.PowerOutletTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='interface_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.InterfaceTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='front_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.FrontPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='rear_port_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.RearPortTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='device_bay_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.DeviceBayTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='module_bay_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.ModuleBayTemplate'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='inventory_item_template_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.InventoryItemTemplate'
            ),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='member_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='virtual_chassis', to_model='dcim.Device'
            ),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='rf_role',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='power_feeds',
                to='tenancy.tenant',
            ),
        ),
        migrations.RenameField(
            model_name='device',
            old_name='device_role',
            new_name='role',
        ),
    ]
