import django.db.models.deletion
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def copy_site_assignments(apps, schema_editor):
    """
    Copy site ForeignKey values to the Termination GFK.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    ProviderNetwork = apps.get_model('circuits', 'ProviderNetwork')
    Site = apps.get_model('dcim', 'Site')
    db_alias = schema_editor.connection.alias

    CircuitTermination.objects.using(db_alias).filter(site__isnull=False).update(
        termination_type=ContentType.objects.get_for_model(Site), termination_id=models.F('site_id')
    )

    CircuitTermination.objects.using(db_alias).filter(provider_network__isnull=False).update(
        termination_type=ContentType.objects.get_for_model(ProviderNetwork),
        termination_id=models.F('provider_network_id'),
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
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        # Copy over existing site assignments
        migrations.RunPython(code=copy_site_assignments, reverse_code=migrations.RunPython.noop),
    ]


def oc_circuittermination_termination(objectchange, reverting):
    site_ct = ContentType.objects.get_by_natural_key('dcim', 'site').pk
    provider_network_ct = ContentType.objects.get_by_natural_key('circuits', 'providernetwork').pk
    for data in (objectchange.prechange_data, objectchange.postchange_data):
        if data is None:
            continue
        if site_id := data.get('site'):
            data.update({
                'termination_type': site_ct,
                'termination_id': site_id,
            })
        elif provider_network_id := data.get('provider_network'):
            data.update({
                'termination_type': provider_network_ct,
                'termination_id': provider_network_id,
            })


objectchange_migrators = {
    'circuits.circuittermination': oc_circuittermination_termination,
}
