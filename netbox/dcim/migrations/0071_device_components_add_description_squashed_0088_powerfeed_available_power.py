import sys

import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

SITE_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'planned'),
    (4, 'retired'),
)

RACK_TYPE_CHOICES = (
    (100, '2-post-frame'),
    (200, '4-post-frame'),
    (300, '4-post-cabinet'),
    (1000, 'wall-frame'),
    (1100, 'wall-cabinet'),
)

RACK_STATUS_CHOICES = (
    (0, 'reserved'),
    (1, 'available'),
    (2, 'planned'),
    (3, 'active'),
    (4, 'deprecated'),
)

RACK_DIMENSION_CHOICES = (
    (1000, 'mm'),
    (2000, 'in'),
)

SUBDEVICE_ROLE_CHOICES = (
    ('true', 'parent'),
    ('false', 'child'),
)

DEVICE_FACE_CHOICES = (
    (0, 'front'),
    (1, 'rear'),
)

DEVICE_STATUS_CHOICES = (
    (0, 'offline'),
    (1, 'active'),
    (2, 'planned'),
    (3, 'staged'),
    (4, 'failed'),
    (5, 'inventory'),
    (6, 'decommissioning'),
)

INTERFACE_TYPE_CHOICES = (
    (0, 'virtual'),
    (200, 'lag'),
    (800, '100base-tx'),
    (1000, '1000base-t'),
    (1050, '1000base-x-gbic'),
    (1100, '1000base-x-sfp'),
    (1120, '2.5gbase-t'),
    (1130, '5gbase-t'),
    (1150, '10gbase-t'),
    (1170, '10gbase-cx4'),
    (1200, '10gbase-x-sfpp'),
    (1300, '10gbase-x-xfp'),
    (1310, '10gbase-x-xenpak'),
    (1320, '10gbase-x-x2'),
    (1350, '25gbase-x-sfp28'),
    (1400, '40gbase-x-qsfpp'),
    (1420, '50gbase-x-sfp28'),
    (1500, '100gbase-x-cfp'),
    (1510, '100gbase-x-cfp2'),
    (1520, '100gbase-x-cfp4'),
    (1550, '100gbase-x-cpak'),
    (1600, '100gbase-x-qsfp28'),
    (1650, '200gbase-x-cfp2'),
    (1700, '200gbase-x-qsfp56'),
    (1750, '400gbase-x-qsfpdd'),
    (1800, '400gbase-x-osfp'),
    (2600, 'ieee802.11a'),
    (2610, 'ieee802.11g'),
    (2620, 'ieee802.11n'),
    (2630, 'ieee802.11ac'),
    (2640, 'ieee802.11ad'),
    (2810, 'gsm'),
    (2820, 'cdma'),
    (2830, 'lte'),
    (6100, 'sonet-oc3'),
    (6200, 'sonet-oc12'),
    (6300, 'sonet-oc48'),
    (6400, 'sonet-oc192'),
    (6500, 'sonet-oc768'),
    (6600, 'sonet-oc1920'),
    (6700, 'sonet-oc3840'),
    (3010, '1gfc-sfp'),
    (3020, '2gfc-sfp'),
    (3040, '4gfc-sfp'),
    (3080, '8gfc-sfpp'),
    (3160, '16gfc-sfpp'),
    (3320, '32gfc-sfp28'),
    (3400, '128gfc-sfp28'),
    (7010, 'inifiband-sdr'),
    (7020, 'inifiband-ddr'),
    (7030, 'inifiband-qdr'),
    (7040, 'inifiband-fdr10'),
    (7050, 'inifiband-fdr'),
    (7060, 'inifiband-edr'),
    (7070, 'inifiband-hdr'),
    (7080, 'inifiband-ndr'),
    (7090, 'inifiband-xdr'),
    (4000, 't1'),
    (4010, 'e1'),
    (4040, 't3'),
    (4050, 'e3'),
    (5000, 'cisco-stackwise'),
    (5050, 'cisco-stackwise-plus'),
    (5100, 'cisco-flexstack'),
    (5150, 'cisco-flexstack-plus'),
    (5200, 'juniper-vcp'),
    (5300, 'extreme-summitstack'),
    (5310, 'extreme-summitstack-128'),
    (5320, 'extreme-summitstack-256'),
    (5330, 'extreme-summitstack-512'),
)

INTERFACE_MODE_CHOICES = (
    (100, 'access'),
    (200, 'tagged'),
    (300, 'tagged-all'),
)

PORT_TYPE_CHOICES = (
    (1000, '8p8c'),
    (1100, '110-punch'),
    (1200, 'bnc'),
    (2000, 'st'),
    (2100, 'sc'),
    (2110, 'sc-apc'),
    (2200, 'fc'),
    (2300, 'lc'),
    (2310, 'lc-apc'),
    (2400, 'mtrj'),
    (2500, 'mpo'),
    (2600, 'lsh'),
    (2610, 'lsh-apc'),
)

CABLE_TYPE_CHOICES = (
    (1300, 'cat3'),
    (1500, 'cat5'),
    (1510, 'cat5e'),
    (1600, 'cat6'),
    (1610, 'cat6a'),
    (1700, 'cat7'),
    (1800, 'dac-active'),
    (1810, 'dac-passive'),
    (1900, 'coaxial'),
    (3000, 'mmf'),
    (3010, 'mmf-om1'),
    (3020, 'mmf-om2'),
    (3030, 'mmf-om3'),
    (3040, 'mmf-om4'),
    (3500, 'smf'),
    (3510, 'smf-os1'),
    (3520, 'smf-os2'),
    (3800, 'aoc'),
    (5000, 'power'),
)

CABLE_STATUS_CHOICES = (
    ('true', 'connected'),
    ('false', 'planned'),
)

CABLE_LENGTH_UNIT_CHOICES = (
    (1200, 'm'),
    (1100, 'cm'),
    (2100, 'ft'),
    (2000, 'in'),
)

POWERFEED_STATUS_CHOICES = (
    (0, 'offline'),
    (1, 'active'),
    (2, 'planned'),
    (4, 'failed'),
)

POWERFEED_TYPE_CHOICES = (
    (1, 'primary'),
    (2, 'redundant'),
)

POWERFEED_SUPPLY_CHOICES = (
    (1, 'ac'),
    (2, 'dc'),
)

POWERFEED_PHASE_CHOICES = (
    (1, 'single-phase'),
    (3, 'three-phase'),
)

POWEROUTLET_FEED_LEG_CHOICES_CHOICES = (
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
)


def cache_cable_devices(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')

    if 'test' not in sys.argv:
        print("\nUpdating cable device terminations...")
    cable_count = Cable.objects.count()

    # Cache A/B termination devices on all existing Cables. Note that the custom save() method on Cable is not
    # available during a migration, so we replicate its logic here.
    for i, cable in enumerate(Cable.objects.all(), start=1):

        if not i % 1000 and 'test' not in sys.argv:
            print("[{}/{}]".format(i, cable_count))

        termination_a_model = apps.get_model(cable.termination_a_type.app_label, cable.termination_a_type.model)
        termination_a_device = None
        if hasattr(termination_a_model, 'device'):
            termination_a = termination_a_model.objects.get(pk=cable.termination_a_id)
            termination_a_device = termination_a.device

        termination_b_model = apps.get_model(cable.termination_b_type.app_label, cable.termination_b_type.model)
        termination_b_device = None
        if hasattr(termination_b_model, 'device'):
            termination_b = termination_b_model.objects.get(pk=cable.termination_b_id)
            termination_b_device = termination_b.device

        Cable.objects.filter(pk=cable.pk).update(
            _termination_a_device=termination_a_device,
            _termination_b_device=termination_b_device
        )


def site_status_to_slug(apps, schema_editor):
    Site = apps.get_model('dcim', 'Site')
    for id, slug in SITE_STATUS_CHOICES:
        Site.objects.filter(status=str(id)).update(status=slug)


def rack_type_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_TYPE_CHOICES:
        Rack.objects.filter(type=str(id)).update(type=slug)


def rack_status_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_STATUS_CHOICES:
        Rack.objects.filter(status=str(id)).update(status=slug)


def rack_outer_unit_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_DIMENSION_CHOICES:
        Rack.objects.filter(status=str(id)).update(status=slug)


def devicetype_subdevicerole_to_slug(apps, schema_editor):
    DeviceType = apps.get_model('dcim', 'DeviceType')
    for boolean, slug in SUBDEVICE_ROLE_CHOICES:
        DeviceType.objects.filter(subdevice_role=boolean).update(subdevice_role=slug)


def device_face_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_FACE_CHOICES:
        Device.objects.filter(face=str(id)).update(face=slug)


def device_status_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_STATUS_CHOICES:
        Device.objects.filter(status=str(id)).update(status=slug)


def interfacetemplate_type_to_slug(apps, schema_editor):
    InterfaceTemplate = apps.get_model('dcim', 'InterfaceTemplate')
    for id, slug in INTERFACE_TYPE_CHOICES:
        InterfaceTemplate.objects.filter(type=id).update(type=slug)


def interface_type_to_slug(apps, schema_editor):
    Interface = apps.get_model('dcim', 'Interface')
    for id, slug in INTERFACE_TYPE_CHOICES:
        Interface.objects.filter(type=id).update(type=slug)


def interface_mode_to_slug(apps, schema_editor):
    Interface = apps.get_model('dcim', 'Interface')
    for id, slug in INTERFACE_MODE_CHOICES:
        Interface.objects.filter(mode=id).update(mode=slug)


def frontporttemplate_type_to_slug(apps, schema_editor):
    FrontPortTemplate = apps.get_model('dcim', 'FrontPortTemplate')
    for id, slug in PORT_TYPE_CHOICES:
        FrontPortTemplate.objects.filter(type=id).update(type=slug)


def rearporttemplate_type_to_slug(apps, schema_editor):
    RearPortTemplate = apps.get_model('dcim', 'RearPortTemplate')
    for id, slug in PORT_TYPE_CHOICES:
        RearPortTemplate.objects.filter(type=id).update(type=slug)


def frontport_type_to_slug(apps, schema_editor):
    FrontPort = apps.get_model('dcim', 'FrontPort')
    for id, slug in PORT_TYPE_CHOICES:
        FrontPort.objects.filter(type=id).update(type=slug)


def rearport_type_to_slug(apps, schema_editor):
    RearPort = apps.get_model('dcim', 'RearPort')
    for id, slug in PORT_TYPE_CHOICES:
        RearPort.objects.filter(type=id).update(type=slug)


def cable_type_to_slug(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')
    for id, slug in CABLE_TYPE_CHOICES:
        Cable.objects.filter(type=id).update(type=slug)


def cable_status_to_slug(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')
    for bool_str, slug in CABLE_STATUS_CHOICES:
        Cable.objects.filter(status=bool_str).update(status=slug)


def cable_length_unit_to_slug(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')
    for id, slug in CABLE_LENGTH_UNIT_CHOICES:
        Cable.objects.filter(length_unit=id).update(length_unit=slug)


def powerfeed_status_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_STATUS_CHOICES:
        PowerFeed.objects.filter(status=id).update(status=slug)


def powerfeed_type_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_TYPE_CHOICES:
        PowerFeed.objects.filter(type=id).update(type=slug)


def powerfeed_supply_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_SUPPLY_CHOICES:
        PowerFeed.objects.filter(supply=id).update(supply=slug)


def powerfeed_phase_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_PHASE_CHOICES:
        PowerFeed.objects.filter(phase=id).update(phase=slug)


def poweroutlettemplate_feed_leg_to_slug(apps, schema_editor):
    PowerOutletTemplate = apps.get_model('dcim', 'PowerOutletTemplate')
    for id, slug in POWEROUTLET_FEED_LEG_CHOICES_CHOICES:
        PowerOutletTemplate.objects.filter(feed_leg=id).update(feed_leg=slug)


def poweroutlet_feed_leg_to_slug(apps, schema_editor):
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')
    for id, slug in POWEROUTLET_FEED_LEG_CHOICES_CHOICES:
        PowerOutlet.objects.filter(feed_leg=id).update(feed_leg=slug)


class Migration(migrations.Migration):

    replaces = [('dcim', '0071_device_components_add_description'), ('dcim', '0072_powerfeeds'), ('dcim', '0073_interface_form_factor_to_type'), ('dcim', '0074_increase_field_length_platform_name_slug'), ('dcim', '0075_cable_devices'), ('dcim', '0076_console_port_types'), ('dcim', '0077_power_types'), ('dcim', '0078_3569_site_fields'), ('dcim', '0079_3569_rack_fields'), ('dcim', '0080_3569_devicetype_fields'), ('dcim', '0081_3569_device_fields'), ('dcim', '0082_3569_interface_fields'), ('dcim', '0082_3569_port_fields'), ('dcim', '0083_3569_cable_fields'), ('dcim', '0084_3569_powerfeed_fields'), ('dcim', '0085_3569_poweroutlet_fields'), ('dcim', '0086_device_name_nonunique'), ('dcim', '0087_role_descriptions'), ('dcim', '0088_powerfeed_available_power')]

    dependencies = [
        ('dcim', '0070_custom_tag_models'),
        ('extras', '0021_add_color_comments_changelog_to_tag'),
        ('tenancy', '0006_custom_tag_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='powerport',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.CreateModel(
            name='PowerPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('rack_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.RackGroup')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dcim.Site')),
            ],
            options={
                'ordering': ['site', 'name'],
                'unique_together': {('site', 'name')},
            },
        ),
        migrations.CreateModel(
            name='PowerFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('type', models.PositiveSmallIntegerField(default=1)),
                ('supply', models.PositiveSmallIntegerField(default=1)),
                ('phase', models.PositiveSmallIntegerField(default=1)),
                ('voltage', models.PositiveSmallIntegerField(default=120, validators=[django.core.validators.MinValueValidator(1)])),
                ('amperage', models.PositiveSmallIntegerField(default=20, validators=[django.core.validators.MinValueValidator(1)])),
                ('max_utilization', models.PositiveSmallIntegerField(default=80, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('available_power', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('comments', models.TextField(blank=True)),
                ('cable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable')),
                ('power_panel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='powerfeeds', to='dcim.PowerPanel')),
                ('rack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.Rack')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags')),
                ('connected_endpoint', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.PowerPort')),
                ('connection_status', models.NullBooleanField()),
            ],
            options={
                'ordering': ['power_panel', 'name'],
                'unique_together': {('power_panel', 'name')},
            },
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='connected_endpoint',
            new_name='_connected_poweroutlet',
        ),
        migrations.AddField(
            model_name='powerport',
            name='_connected_powerfeed',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.PowerFeed'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='allocated_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerport',
            name='maximum_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='allocated_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='maximum_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlets', to='dcim.PowerPort'),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlet_templates', to='dcim.PowerPortTemplate'),
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='form_factor',
            new_name='type',
        ),
        migrations.RenameField(
            model_name='interfacetemplate',
            old_name='form_factor',
            new_name='type',
        ),
        migrations.AlterField(
            model_name='platform',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='cable',
            name='_termination_a_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='cable',
            name='_termination_b_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.Device'),
        ),
        migrations.RunPython(
            code=cache_cable_devices,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.AddField(
            model_name='consoleport',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='powerport',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='site',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=site_status_to_slug,
        ),
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=rack_type_to_slug,
        ),
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='rack',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=rack_status_to_slug,
        ),
        migrations.AlterField(
            model_name='rack',
            name='outer_unit',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=rack_outer_unit_to_slug,
        ),
        migrations.AlterField(
            model_name='rack',
            name='outer_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=devicetype_subdevicerole_to_slug,
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=device_face_to_slug,
        ),
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=device_status_to_slug,
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=interfacetemplate_type_to_slug,
        ),
        migrations.AlterField(
            model_name='interface',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=interface_type_to_slug,
        ),
        migrations.AlterField(
            model_name='interface',
            name='mode',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=interface_mode_to_slug,
        ),
        migrations.AlterField(
            model_name='interface',
            name='mode',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=frontporttemplate_type_to_slug,
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=rearporttemplate_type_to_slug,
        ),
        migrations.AlterField(
            model_name='frontport',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=frontport_type_to_slug,
        ),
        migrations.AlterField(
            model_name='rearport',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=rearport_type_to_slug,
        ),
        migrations.AlterField(
            model_name='cable',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=cable_type_to_slug,
        ),
        migrations.AlterField(
            model_name='cable',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='cable',
            name='status',
            field=models.CharField(default='connected', max_length=50),
        ),
        migrations.RunPython(
            code=cable_status_to_slug,
        ),
        migrations.AlterField(
            model_name='cable',
            name='length_unit',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=cable_length_unit_to_slug,
        ),
        migrations.AlterField(
            model_name='cable',
            name='length_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_status_to_slug,
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='type',
            field=models.CharField(default='primary', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_type_to_slug,
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='supply',
            field=models.CharField(default='ac', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_supply_to_slug,
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='phase',
            field=models.CharField(default='single-phase', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_phase_to_slug,
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=poweroutlettemplate_feed_leg_to_slug,
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=poweroutlet_feed_leg_to_slug,
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('rack', 'position', 'face'), ('site', 'tenant', 'name'), ('virtual_chassis', 'vc_position')},
        ),
        migrations.AddField(
            model_name='devicerole',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='available_power',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
