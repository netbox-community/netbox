import django.db.models.deletion
from django.db import migrations, models


def copy_site_assignments(apps, schema_editor):
    """
    Copy site ForeignKey values to the Termination GFK.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    Site = apps.get_model('dcim', 'Site')

    CircuitTermination.objects.filter(site__isnull=False).update(
        termination_type=ContentType.objects.get_for_model(Site),
        termination_id=models.F('site_id')
    )

    ProviderNetwork = apps.get_model('circuits', 'ProviderNetwork')
    CircuitTermination.objects.filter(provider_network__isnull=False).update(
        termination_type=ContentType.objects.get_for_model(ProviderNetwork),
        termination_id=models.F('provider_network_id')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0046_charfield_null_choices'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0193_poweroutlet_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='termination_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='termination_type',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(('model__in', ('region', 'sitegroup', 'site', 'location', 'providernetwork'))),
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
