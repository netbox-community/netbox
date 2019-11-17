from django.db import migrations, models

DEVICE_FACE_CHOICES = (
    (0, 'front'),
    (1, 'rear'),
)


def rack_type_to_slug(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for id, slug in DEVICE_FACE_CHOICES:
        Device.objects.filter(face=str(id)).update(face=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0078_rack_choicefields_to_slugs'),
    ]

    operations = [
        # Device.face
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            code=rack_type_to_slug
        ),
    ]
