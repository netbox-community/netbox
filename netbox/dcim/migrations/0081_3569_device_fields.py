from django.db import migrations, models

DEVICE_FACE_CHOICES = (
    (0, 'front'),
    (1, 'rear'),
)


def device_face_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_FACE_CHOICES:
        Device.objects.filter(face=str(id)).update(face=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0080_3569_devicetype_fields'),
    ]

    operations = [
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
    ]
