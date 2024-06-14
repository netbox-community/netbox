import django.db.models.functions.text
import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('dcim', '0160_populate_cable_ends'),
        ('dcim', '0161_cabling_cleanup'),
        ('dcim', '0162_unique_constraints'),
        ('dcim', '0163_weight_fields'),
        ('dcim', '0164_rack_mounting_depth'),
        ('dcim', '0165_standardize_description_comments'),
        ('dcim', '0166_virtualdevicecontext')
    ]

    dependencies = [
        ('ipam', '0047_squashed_0053'),
        ('tenancy', '0009_standardize_description_comments'),
        ('circuits', '0037_new_cabling_models'),
        ('dcim', '0159_populate_cable_paths'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cable',
            options={'ordering': ('pk',)},
        ),
        migrations.AlterUniqueTogether(
            name='cable',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_a_id',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_a_type',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_b_id',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_b_type',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='_termination_a_device',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='_termination_b_device',
        ),
        migrations.AlterUniqueTogether(
            name='cablepath',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='destination_id',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='destination_type',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='origin_id',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='origin_type',
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='rearport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='rearport',
            name='_link_peer_type',
        ),
        migrations.RemoveConstraint(
            model_name='cabletermination',
            name='dcim_cable_termination_unique_termination',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_name',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_slug',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_name',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_slug',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_name',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_slug',
        ),
        migrations.AlterUniqueTogether(
            name='consoleport',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='consoleporttemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='consoleserverport',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='consoleserverporttemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='devicebay',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='devicebaytemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='devicetype',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='frontport',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='frontporttemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='interface',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='interfacetemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='inventoryitem',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='inventoryitemtemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='modulebay',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='modulebaytemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='moduletype',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='powerfeed',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='poweroutlet',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='poweroutlettemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='powerpanel',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='powerport',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='powerporttemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='rack',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='rearport',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='rearporttemplate',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(fields=('termination_type', 'termination_id'), name='dcim_cabletermination_unique_termination'),
        ),
        migrations.AddConstraint(
            model_name='consoleport',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_consoleport_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='consoleporttemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_consoleporttemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='consoleporttemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_consoleporttemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='consoleserverport',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_consoleserverport_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='consoleserverporttemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_consoleserverporttemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='consoleserverporttemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_consoleserverporttemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('site'), models.F('tenant'), name='dcim_device_unique_name_site_tenant'),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('site'), condition=models.Q(('tenant__isnull', True)), name='dcim_device_unique_name_site', violation_error_message='Device name must be unique per site.'),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(fields=('rack', 'position', 'face'), name='dcim_device_unique_rack_position_face'),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(fields=('virtual_chassis', 'vc_position'), name='dcim_device_unique_virtual_chassis_vc_position'),
        ),
        migrations.AddConstraint(
            model_name='devicebay',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_devicebay_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='devicebaytemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_devicebaytemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='devicetype',
            constraint=models.UniqueConstraint(fields=('manufacturer', 'model'), name='dcim_devicetype_unique_manufacturer_model'),
        ),
        migrations.AddConstraint(
            model_name='devicetype',
            constraint=models.UniqueConstraint(fields=('manufacturer', 'slug'), name='dcim_devicetype_unique_manufacturer_slug'),
        ),
        migrations.AddConstraint(
            model_name='frontport',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_frontport_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='frontport',
            constraint=models.UniqueConstraint(fields=('rear_port', 'rear_port_position'), name='dcim_frontport_unique_rear_port_position'),
        ),
        migrations.AddConstraint(
            model_name='frontporttemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_frontporttemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='frontporttemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_frontporttemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='frontporttemplate',
            constraint=models.UniqueConstraint(fields=('rear_port', 'rear_port_position'), name='dcim_frontporttemplate_unique_rear_port_position'),
        ),
        migrations.AddConstraint(
            model_name='interface',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_interface_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='interfacetemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_interfacetemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='interfacetemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_interfacetemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='inventoryitem',
            constraint=models.UniqueConstraint(fields=('device', 'parent', 'name'), name='dcim_inventoryitem_unique_device_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='inventoryitemtemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'parent', 'name'), name='dcim_inventoryitemtemplate_unique_device_type_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('site', 'name'), name='dcim_location_name', violation_error_message='A location with this name already exists within the specified site.'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('site', 'slug'), name='dcim_location_slug', violation_error_message='A location with this slug already exists within the specified site.'),
        ),
        migrations.AddConstraint(
            model_name='modulebay',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_modulebay_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='modulebaytemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_modulebaytemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='moduletype',
            constraint=models.UniqueConstraint(fields=('manufacturer', 'model'), name='dcim_moduletype_unique_manufacturer_model'),
        ),
        migrations.AddConstraint(
            model_name='powerfeed',
            constraint=models.UniqueConstraint(fields=('power_panel', 'name'), name='dcim_powerfeed_unique_power_panel_name'),
        ),
        migrations.AddConstraint(
            model_name='poweroutlet',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_poweroutlet_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='poweroutlettemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_poweroutlettemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='poweroutlettemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_poweroutlettemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='powerpanel',
            constraint=models.UniqueConstraint(fields=('site', 'name'), name='dcim_powerpanel_unique_site_name'),
        ),
        migrations.AddConstraint(
            model_name='powerport',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_powerport_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='powerporttemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_powerporttemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='powerporttemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_powerporttemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='rack',
            constraint=models.UniqueConstraint(fields=('location', 'name'), name='dcim_rack_unique_location_name'),
        ),
        migrations.AddConstraint(
            model_name='rack',
            constraint=models.UniqueConstraint(fields=('location', 'facility_id'), name='dcim_rack_unique_location_facility_id'),
        ),
        migrations.AddConstraint(
            model_name='rearport',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_rearport_unique_device_name'),
        ),
        migrations.AddConstraint(
            model_name='rearporttemplate',
            constraint=models.UniqueConstraint(fields=('device_type', 'name'), name='dcim_rearporttemplate_unique_device_type_name'),
        ),
        migrations.AddConstraint(
            model_name='rearporttemplate',
            constraint=models.UniqueConstraint(fields=('module_type', 'name'), name='dcim_rearporttemplate_unique_module_type_name'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('name',), name='dcim_region_name', violation_error_message='A top-level region with this name already exists.'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('slug',), name='dcim_region_slug', violation_error_message='A top-level region with this slug already exists.'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('name',), name='dcim_sitegroup_name', violation_error_message='A top-level site group with this name already exists.'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(condition=models.Q(('parent__isnull', True)), fields=('slug',), name='dcim_sitegroup_slug', violation_error_message='A top-level site group with this slug already exists.'),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='max_weight',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='rack',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='_abs_max_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='mounting_depth',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cable',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='cable',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='device',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='module',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='rack',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.CreateModel(
            name='VirtualDeviceContext',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=64)),
                ('status', models.CharField(max_length=50)),
                ('identifier', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('comments', models.TextField(blank=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vdcs', to='dcim.device')),
                ('primary_ip4', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('primary_ip6', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vdcs', to='tenancy.tenant')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='interface',
            name='vdcs',
            field=models.ManyToManyField(related_name='interfaces', to='dcim.virtualdevicecontext'),
        ),
        migrations.AddConstraint(
            model_name='virtualdevicecontext',
            constraint=models.UniqueConstraint(fields=('device', 'identifier'), name='dcim_virtualdevicecontext_device_identifier'),
        ),
        migrations.AddConstraint(
            model_name='virtualdevicecontext',
            constraint=models.UniqueConstraint(fields=('device', 'name'), name='dcim_virtualdevicecontext_device_name'),
        ),
    ]
