from django.db import migrations, models


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


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0082_3569_port_fields'),
    ]

    operations = [

        # Cable.type
        migrations.AlterField(
            model_name='cable',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=cable_type_to_slug
        ),
        migrations.AlterField(
            model_name='cable',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),

        # Cable.status
        migrations.AlterField(
            model_name='cable',
            name='status',
            field=models.CharField(default='connected', max_length=50),
        ),
        migrations.RunPython(
            code=cable_status_to_slug
        ),

        # Cable.length_unit
        migrations.AlterField(
            model_name='cable',
            name='length_unit',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=cable_length_unit_to_slug
        ),
        migrations.AlterField(
            model_name='cable',
            name='length_unit',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
