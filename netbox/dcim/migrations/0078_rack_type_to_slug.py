from django.db import migrations, models

RACK_TYPE_CHOICES = (
    (100, '2-post-frame'),
    (200, '4-post-frame'),
    (300, '4-post-cabinet'),
    (1000, 'wall-frame'),
    (1100, 'wall-cabinet'),
)


def rack_type_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_TYPE_CHOICES:
        Rack.objects.filter(type=str(id)).update(type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0077_power_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=rack_type_to_slug
        ),
    ]
