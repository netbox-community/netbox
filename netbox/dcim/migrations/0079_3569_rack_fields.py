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

RACK_DIMENSION_CHOICES = (
    (1000, 'mm'),
    (2000, 'in'),
)


def rack_type_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_TYPE_CHOICES:
        Rack.objects.filter(type=str(id)).update(type=slug)


def rack_status_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_STATUS_CHOICES:
        Rack.objects.filter(status=str(id)).update(status=slug)


def rack_outer_unit_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_DIMENSION_CHOICES:
        Rack.objects.filter(outer_unit=str(id)).update(outer_unit=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0078_3569_site_fields'),
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
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),

        # Rack.status
        migrations.AlterField(
            model_name='rack',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=rack_status_to_slug
        ),

        # Rack.outer_unit
        migrations.AlterField(
            model_name='rack',
            name='outer_unit',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=rack_outer_unit_to_slug
        ),
        migrations.AlterField(
            model_name='rack',
            name='outer_unit',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
