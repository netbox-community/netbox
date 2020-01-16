from django.db import migrations, models

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


def device_face_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_FACE_CHOICES:
        Device.objects.filter(face=str(id)).update(face=slug)


def device_status_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_STATUS_CHOICES:
        Device.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0080_3569_devicetype_fields'),
    ]

    operations = [

        # Device.face
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=device_face_to_slug
        ),
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, max_length=50),
        ),

        # Device.status
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=device_status_to_slug
        ),

    ]
