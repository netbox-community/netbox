from django.db import migrations, models


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


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0081_3569_device_fields'),
    ]

    operations = [

        # InterfaceTemplate.type
        migrations.AlterField(
            model_name='interfacetemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=interfacetemplate_type_to_slug
        ),

        # Interface.type
        migrations.AlterField(
            model_name='interface',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=interface_type_to_slug
        ),

        # Interface.mode
        migrations.AlterField(
            model_name='interface',
            name='mode',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=interface_mode_to_slug
        ),
        migrations.AlterField(
            model_name='interface',
            name='mode',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
