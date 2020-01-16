import django.contrib.postgres.fields.jsonb
import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('dcim', '0062_interface_mtu'), ('dcim', '0063_device_local_context_data'), ('dcim', '0064_remove_platform_rpc_client'), ('dcim', '0065_front_rear_ports')]

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('dcim', '0061_platform_napalm_args'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='mtu',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65536)], verbose_name='MTU'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1510, 'CFP2 (100GE)'], [1520, 'CFP4 (100GE)'], [1550, 'Cisco CPAK (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['SONET', [[6100, 'OC-3/STM-1'], [6200, 'OC-12/STM-4'], [6300, 'OC-48/STM-16'], [6400, 'OC-192/STM-64'], [6500, 'OC-768/STM-256'], [6600, 'OC-1920/STM-640'], [6700, 'OC-3840/STM-1234']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)'], [3320, 'SFP28 (32GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP'], [5300, 'Extreme SummitStack'], [5310, 'Extreme SummitStack-128'], [5320, 'Extreme SummitStack-256'], [5330, 'Extreme SummitStack-512']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1510, 'CFP2 (100GE)'], [1520, 'CFP4 (100GE)'], [1550, 'Cisco CPAK (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['SONET', [[6100, 'OC-3/STM-1'], [6200, 'OC-12/STM-4'], [6300, 'OC-48/STM-16'], [6400, 'OC-192/STM-64'], [6500, 'OC-768/STM-256'], [6600, 'OC-1920/STM-640'], [6700, 'OC-3840/STM-1234']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)'], [3320, 'SFP28 (32GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP'], [5300, 'Extreme SummitStack'], [5310, 'Extreme SummitStack-128'], [5320, 'Extreme SummitStack-256'], [5330, 'Extreme SummitStack-512']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AddField(
            model_name='device',
            name='local_context_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='platform',
            name='rpc_client',
        ),
        migrations.CreateModel(
            name='RearPort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('positions', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('description', models.CharField(blank=True, max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearports', to='dcim.Device')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['device', 'name'],
                'unique_together': {('device', 'name')},
            },
        ),
        migrations.CreateModel(
            name='RearPortTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('positions', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearport_templates', to='dcim.DeviceType')),
            ],
            options={
                'ordering': ['device_type', 'name'],
                'unique_together': {('device_type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='FrontPortTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('rear_port_position', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontport_templates', to='dcim.DeviceType')),
                ('rear_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontport_templates', to='dcim.RearPortTemplate')),
            ],
            options={
                'ordering': ['device_type', 'name'],
                'unique_together': {('rear_port', 'rear_port_position'), ('device_type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='FrontPort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('rear_port_position', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('description', models.CharField(blank=True, max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontports', to='dcim.Device')),
                ('rear_port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontports', to='dcim.RearPort')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['device', 'name'],
                'unique_together': {('device', 'name'), ('rear_port', 'rear_port_position')},
            },
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleport_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleserverport_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlet_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerport_templates', to='dcim.DeviceType'),
        ),
    ]
