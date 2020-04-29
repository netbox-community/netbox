from django.db import migrations

RACK_DIMENSION_CHOICES = (
    (1000, 'mm'),
    (2000, 'in'),
)


def rack_outer_unit_to_slug(apps, schema_editor):
    Rack = apps.get_model('dcim', 'Rack')
    for id, slug in RACK_DIMENSION_CHOICES:
        Rack.objects.filter(outer_unit=str(id)).update(outer_unit=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0091_interface_type_other'),
    ]

    operations = [
        # Fixes a missed field migration from #3569; see bug #4056. The original migration has also been fixed.
        migrations.RunPython(
            code=rack_outer_unit_to_slug
        ),
    ]
