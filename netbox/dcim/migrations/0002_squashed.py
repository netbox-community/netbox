from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    replaces = [
        ('dcim', '0002_auto_20160622_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualchassis',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='sitegroup',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.sitegroup'),
        ),
        migrations.AddField(
            model_name='site',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='dcim.sitegroup'),
        ),
        migrations.AddField(
            model_name='site',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='dcim.region'),
        ),
        migrations.AddField(
            model_name='site',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='site',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sites', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='region',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.region'),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearporttemplates', to='dcim.devicetype'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearports', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='rack',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='dcim.rack'),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rackreservations', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rack',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='racks', to='dcim.location'),
        ),
        migrations.AddField(
            model_name='rack',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='racks', to='dcim.rackrole'),
        ),
        migrations.AddField(
            model_name='rack',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='racks', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='rack',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='rack',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='racks', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerporttemplates', to='dcim.devicetype'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerports', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.location'),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dcim.site'),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlettemplates', to='dcim.devicetype'),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlet_templates', to='dcim.powerporttemplate'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlets', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlets', to='dcim.powerport'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='power_panel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='powerfeeds', to='dcim.powerpanel'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='rack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.rack'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='platform',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='platforms', to='dcim.manufacturer'),
        ),
        migrations.AddField(
            model_name='location',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.location'),
        ),
        migrations.AddField(
            model_name='location',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventoryitems', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_items', to='dcim.manufacturer'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_items', to='dcim.inventoryitem'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfacetemplates', to='dcim.devicetype'),
        ),
        migrations.AddField(
            model_name='interface',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='interface',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='interface',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='interface',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='interface',
            name='lag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_interfaces', to='dcim.interface'),
        ),
        migrations.AddField(
            model_name='interface',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_interfaces', to='dcim.interface'),
        ),
    ]
