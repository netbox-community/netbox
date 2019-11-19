from django.db import migrations, models

RACK_TYPE_CHOICES = (
    (100, '2-post-frame'),
    (200, '4-post-frame'),
    (300, '4-post-cabinet'),
    (1000, 'wall-frame'),
    (1100, 'wall-cabinet'),
)

RACK_STATUS_CHOICES = (
    (0, 'reserved'),
    (1, 'available'),
    (2, 'planned'),
    (3, 'active'),
    (4, 'deprecated'),
)


def rack_type_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_TYPE_CHOICES:
        Rack.objects.filter(type=str(id)).update(type=slug)


def rack_status_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_STATUS_CHOICES:
        Rack.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0077_power_types'),
    ]

    operations = [
        # Rack.type
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=rack_type_to_slug
        ),
        # Rack.status
        migrations.AlterField(
            model_name='rack',
            name='status',
            field=models.CharField(blank=True, default='active', max_length=50),
        ),
        migrations.RunPython(
            code=rack_status_to_slug
        ),
    ]
