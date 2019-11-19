from django.db import migrations, models

RACK_STATUS_CHOICES = (
    (0, 'reserved'),
    (1, 'available'),
    (2, 'planned'),
    (3, 'active'),
    (4, 'deprecated'),
)


def rack_status_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_STATUS_CHOICES:
        Rack.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0078_rack_type_to_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rack',
            name='status',
            field=models.CharField(blank=True, default='active', max_length=50),
        ),
        migrations.RunPython(
            code=rack_status_to_slug
        ),
    ]
