from django.db import migrations

from utilities.utils import to_meters


def recalculate_abs_length(apps, schema_editor):
    """
    Recalculate absolute lengths for all cables with a length and length unit defined. Fixes
    incorrectly calculated values as reported under bug #8377.
    """
    Cable = apps.get_model('dcim', 'Cable')

    cables = Cable.objects.filter(length__isnull=False).exclude(length_unit='')
    for cable in cables:
        cable._abs_length = to_meters(cable.length, cable.length_unit)

    Cable.objects.bulk_update(cables, ['_abs_length'], batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0143_remove_primary_for_related_name'),
    ]

    operations = [
        migrations.RunPython(
            code=recalculate_abs_length,
            reverse_code=migrations.RunPython.noop
        ),
    ]
