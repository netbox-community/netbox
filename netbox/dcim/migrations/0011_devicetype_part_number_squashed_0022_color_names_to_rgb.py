import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import utilities.fields

COLOR_CONVERSION = {
    'teal': '009688',
    'green': '4caf50',
    'blue': '2196f3',
    'purple': '9c27b0',
    'yellow': 'ffeb3b',
    'orange': 'ff9800',
    'red': 'f44336',
    'light_gray': 'c0c0c0',
    'medium_gray': '9e9e9e',
    'dark_gray': '607d8b',
}


def color_names_to_rgb(apps, schema_editor):
    RackRole = apps.get_model('dcim', 'RackRole')
    DeviceRole = apps.get_model('dcim', 'DeviceRole')
    for color_name, color_rgb in COLOR_CONVERSION.items():
        RackRole.objects.filter(color=color_name).update(color=color_rgb)
        DeviceRole.objects.filter(color=color_name).update(color=color_rgb)


class Migration(migrations.Migration):

    replaces = [('dcim', '0011_devicetype_part_number'), ('dcim', '0012_site_rack_device_add_tenant'), ('dcim', '0013_add_interface_form_factors'), ('dcim', '0014_rack_add_type_width'), ('dcim', '0015_rack_add_u_height_validator'), ('dcim', '0016_module_add_manufacturer'), ('dcim', '0017_rack_add_role'), ('dcim', '0018_device_add_asset_tag'), ('dcim', '0019_new_iface_form_factors'), ('dcim', '0020_rack_desc_units'), ('dcim', '0021_add_ff_flexstack'), ('dcim', '0022_color_names_to_rgb')]

    dependencies = [
        ('dcim', '0010_devicebay_installed_device_set_null'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='part_number',
            field=models.CharField(blank=True, help_text=b'Discrete part number (optional)', max_length=50),
        ),
        migrations.AddField(
            model_name='device',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='tenancy.Tenant'),
        ),
        migrations.AddField(
            model_name='rack',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='racks', to='tenancy.Tenant'),
        ),
        migrations.AddField(
            model_name='site',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sites', to='tenancy.Tenant'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet', [[800, b'100BASE-TX (10/100M)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Modular', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1300, b'XFP (10GE)'], [1200, b'SFP+ (10GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet', [[800, b'100BASE-TX (10/100M)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Modular', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1300, b'XFP (10GE)'], [1200, b'SFP+ (10GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus']]]], default=1200),
        ),
        migrations.AddField(
            model_name='rack',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(100, b'2-post frame'), (200, b'4-post frame'), (300, b'4-post cabinet'), (1000, b'Wall-mounted frame'), (1100, b'Wall-mounted cabinet')], null=True, verbose_name=b'Type'),
        ),
        migrations.AddField(
            model_name='rack',
            name='width',
            field=models.PositiveSmallIntegerField(choices=[(19, b'19 inches'), (23, b'23 inches')], default=19, help_text=b'Rail-to-rail width', verbose_name=b'Width'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='u_height',
            field=models.PositiveSmallIntegerField(default=42, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name=b'Height (U)'),
        ),
        migrations.AddField(
            model_name='module',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modules', to='dcim.Manufacturer'),
        ),
        migrations.CreateModel(
            name='RackRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('color', models.CharField(choices=[[b'teal', b'Teal'], [b'green', b'Green'], [b'blue', b'Blue'], [b'purple', b'Purple'], [b'yellow', b'Yellow'], [b'orange', b'Orange'], [b'red', b'Red'], [b'light_gray', b'Light Gray'], [b'medium_gray', b'Medium Gray'], [b'dark_gray', b'Dark Gray']], max_length=30)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='rack',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='racks', to='dcim.RackRole'),
        ),
        migrations.AddField(
            model_name='device',
            name='asset_tag',
            field=utilities.fields.NullableCharField(blank=True, help_text=b'A unique tag used to identify this device', max_length=50, null=True, unique=True, verbose_name=b'Asset tag'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AddField(
            model_name='rack',
            name='desc_units',
            field=models.BooleanField(default=False, help_text=b'Units are numbered top-to-bottom', verbose_name=b'Descending units'),
        ),
        migrations.AlterField(
            model_name='device',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, help_text=b'The lowest-numbered unit occupied by the device', null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name=b'Position (U)'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.RunPython(
            code=color_names_to_rgb,
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='color',
            field=utilities.fields.ColorField(max_length=6),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='color',
            field=utilities.fields.ColorField(max_length=6),
        ),
    ]
