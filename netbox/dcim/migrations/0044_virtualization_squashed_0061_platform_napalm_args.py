import django.contrib.postgres.fields.jsonb
import django.core.validators
import django.db.models.deletion
import taggit.managers
import timezone_field.fields
from django.conf import settings
from django.db import migrations, models

import utilities.fields


class Migration(migrations.Migration):

    replaces = [('dcim', '0044_virtualization'), ('dcim', '0045_devicerole_vm_role'), ('dcim', '0046_rack_lengthen_facility_id'), ('dcim', '0047_more_100ge_form_factors'), ('dcim', '0048_rack_serial'), ('dcim', '0049_rackreservation_change_user'), ('dcim', '0050_interface_vlan_tagging'), ('dcim', '0051_rackreservation_tenant'), ('dcim', '0052_virtual_chassis'), ('dcim', '0053_platform_manufacturer'), ('dcim', '0054_site_status_timezone_description'), ('dcim', '0055_virtualchassis_ordering'), ('dcim', '0056_django2'), ('dcim', '0057_tags'), ('dcim', '0058_relax_rack_naming_constraints'), ('dcim', '0059_site_latitude_longitude'), ('dcim', '0060_change_logging'), ('dcim', '0061_platform_napalm_args')]

    dependencies = [
        ('virtualization', '0001_virtualization'),
        ('tenancy', '0003_unicode_literals'),
        ('ipam', '0020_ipaddress_add_role_carp'),
        ('dcim', '0043_device_component_name_lengths'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devices', to='virtualization.Cluster'),
        ),
        migrations.AddField(
            model_name='interface',
            name='virtual_machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='virtualization.VirtualMachine'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='vm_role',
            field=models.BooleanField(default=True, help_text='Virtual machines may be assigned to this role', verbose_name='VM Role'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='facility_id',
            field=utilities.fields.NullableCharField(blank=True, max_length=50, null=True, verbose_name='Facility ID'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1510, 'CFP2 (100GE)'], [1520, 'CFP4 (100GE)'], [1550, 'Cisco CPAK (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1510, 'CFP2 (100GE)'], [1520, 'CFP4 (100GE)'], [1550, 'Cisco CPAK (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AddField(
            model_name='rack',
            name='serial',
            field=models.CharField(blank=True, max_length=50, verbose_name='Serial number'),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='interface',
            name='mode',
            field=models.PositiveSmallIntegerField(blank=True, choices=[[100, 'Access'], [200, 'Tagged'], [300, 'Tagged All']], null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='tagged_vlans',
            field=models.ManyToManyField(blank=True, related_name='interfaces_as_tagged', to='ipam.VLAN', verbose_name='Tagged VLANs'),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rackreservations', to='tenancy.Tenant'),
        ),
        migrations.CreateModel(
            name='VirtualChassis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(blank=True, max_length=30)),
                ('master', models.OneToOneField(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='vc_master_for', to='dcim.Device')),
            ],
            options={
                'ordering': ['master'],
                'verbose_name_plural': 'virtual chassis',
            },
        ),
        migrations.AddField(
            model_name='device',
            name='virtual_chassis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='dcim.VirtualChassis'),
        ),
        migrations.AddField(
            model_name='device',
            name='vc_position',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)]),
        ),
        migrations.AddField(
            model_name='device',
            name='vc_priority',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)]),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('rack', 'position', 'face'), ('virtual_chassis', 'vc_position')},
        ),
        migrations.AlterField(
            model_name='platform',
            name='napalm_driver',
            field=models.CharField(blank=True, help_text='The name of the NAPALM driver to use when interacting with devices', max_length=50, verbose_name='NAPALM driver'),
        ),
        migrations.AddField(
            model_name='site',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='site',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[1, 'Active'], [2, 'Planned'], [4, 'Retired']], default=1),
        ),
        migrations.AddField(
            model_name='site',
            name='time_zone',
            field=timezone_field.fields.TimeZoneField(blank=True),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='master',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='vc_master_for', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='interface',
            name='untagged_vlan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interfaces_as_untagged', to='ipam.VLAN', verbose_name='Untagged VLAN'),
        ),
        migrations.AddField(
            model_name='platform',
            name='manufacturer',
            field=models.ForeignKey(blank=True, help_text='Optionally limit this platform to devices of a certain manufacturer', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='platforms', to='dcim.Manufacturer'),
        ),
        migrations.AddField(
            model_name='device',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='rack',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='site',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='interface',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterModelOptions(
            name='rack',
            options={'ordering': ['site', 'group', 'name']},
        ),
        migrations.AlterUniqueTogether(
            name='rack',
            unique_together={('group', 'name'), ('group', 'facility_id')},
        ),
        migrations.AddField(
            model_name='site',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='platform',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='platform',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='region',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='region',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='platform',
            name='napalm_args',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='Additional arguments to pass when initiating the NAPALM driver (JSON format)', null=True, verbose_name='NAPALM arguments'),
        ),
    ]
