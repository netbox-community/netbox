from django.db import migrations, models

SUBDEVICE_ROLE_CHOICES = (
    ('true', 'parent'),
    ('false', 'child'),
)


def devicetype_subdevicerole_to_slug(apps, schema_editor):
    DeviceType = apps.get_model('dcim', 'DeviceType')
    for boolean, slug in SUBDEVICE_ROLE_CHOICES:
        DeviceType.objects.filter(subdevice_role=boolean).update(subdevice_role=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0079_3569_rack_fields'),
    ]

    operations = [

        # DeviceType.subdevice_role
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=devicetype_subdevicerole_to_slug
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
