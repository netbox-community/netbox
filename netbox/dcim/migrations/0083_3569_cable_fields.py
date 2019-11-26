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


def cable_type_to_slug(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')
    for id, slug in CABLE_TYPE_CHOICES:
        Cable.objects.filter(type=id).update(type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0082_3569_port_fields'),
    ]

    operations = [
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
    ]
