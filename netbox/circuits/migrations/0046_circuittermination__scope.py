import django.db.models.deletion
from django.db import migrations, models


def copy_site_assignments(apps, schema_editor):
    """
    Copy site ForeignKey values to the scope GFK.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    Site = apps.get_model('dcim', 'Site')

    CircuitTermination.objects.filter(site__isnull=False).update(
        scope_type=ContentType.objects.get_for_model(Site),
        scope_id=models.F('site_id')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0045_circuit_distance'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0193_poweroutlet_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='scope_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='scope_type',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(('model__in', ('region', 'sitegroup', 'site', 'location'))),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),

        # Copy over existing site assignments
        migrations.RunPython(
            code=copy_site_assignments,
            reverse_code=migrations.RunPython.noop
        ),
    ]
