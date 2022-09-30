from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0161_cabling_cleanup'),
    ]

    operations = [
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
    ]
