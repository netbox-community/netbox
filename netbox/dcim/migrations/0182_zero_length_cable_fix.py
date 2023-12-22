from django.db import migrations


def update_cable_lengths(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')

    # Set the absolute length for any zero-length Cables
    Cable.objects.filter(length=0).update(_abs_length=0)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0181_rename_device_role_device_role'),
    ]

    operations = [
        migrations.RunPython(
            code=update_cable_lengths,
            reverse_code=migrations.RunPython.noop
        ),
    ]
