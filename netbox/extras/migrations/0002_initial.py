from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0002_initial'),
        ('extras', '0001_initial'),
        ('virtualization', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='configcontext',
            name='cluster_groups',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_cluster_groups_+', to='virtualization.ClusterGroup'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='clusters',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_clusters_+', to='virtualization.Cluster'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='device_types',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_device_types_+', to='dcim.DeviceType'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='platforms',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_platforms_+', to='dcim.Platform'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='regions',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_regions_+', to='dcim.Region'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_roles_+', to='dcim.DeviceRole'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='site_groups',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_site_groups_+', to='dcim.SiteGroup'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='sites',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_sites_+', to='dcim.Site'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_tags_+', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='tenant_groups',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_tenant_groups_+', to='tenancy.TenantGroup'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='tenants',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_tenants_+', to='tenancy.Tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='webhook',
            unique_together={('payload_url', 'type_create', 'type_update', 'type_delete')},
        ),
        migrations.AlterIndexTogether(
            name='taggeditem',
            index_together={('content_type', 'object_id')},
        ),
        migrations.AlterUniqueTogether(
            name='exporttemplate',
            unique_together={('content_type', 'name')},
        ),
    ]
