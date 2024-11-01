import django.db.models.deletion
from django.db import migrations, models


def populate_denormalized_fields(apps, schema_editor):
    """
    Copy the denormalized fields for _region, _site_group and _site from existing site field.
    """
    Cluster = apps.get_model('virtualization', 'Cluster')

    clusters = Cluster.objects.filter(site__isnull=False).prefetch_related('site')
    for cluster in clusters:
        cluster._region_id = cluster.site.region_id
        cluster._site_group_id = cluster.site.group_id
        cluster._site_id = cluster.site_id
        # Note: Location cannot be set prior to migration

    Cluster.objects.bulk_update(clusters, ['_region', '_site_group', '_site'])


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0044_cluster_scope'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='_location',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='_%(class)ss',
                to='dcim.location',
            ),
        ),
        migrations.AddField(
            model_name='cluster',
            name='_region',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='_%(class)ss',
                to='dcim.region',
            ),
        ),
        migrations.AddField(
            model_name='cluster',
            name='_site',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='_%(class)ss',
                to='dcim.site',
            ),
        ),
        migrations.AddField(
            model_name='cluster',
            name='_site_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='_%(class)ss',
                to='dcim.sitegroup',
            ),
        ),

        # Populate denormalized FK values
        migrations.RunPython(
            code=populate_denormalized_fields,
            reverse_code=migrations.RunPython.noop
        ),

        migrations.RemoveConstraint(
            model_name='cluster',
            name='virtualization_cluster_unique_site_name',
        ),
        # Delete the site ForeignKey
        migrations.RemoveField(
            model_name='cluster',
            name='site',
        ),
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(
                fields=('_site', 'name'), name='virtualization_cluster_unique__site_name'
            ),
        ),
    ]
