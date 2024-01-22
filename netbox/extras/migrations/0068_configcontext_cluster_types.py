from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0145_site_remove_deprecated_fields'),
        ('virtualization', '0026_vminterface_bridge'),
        ('extras', '0067_customfield_min_max_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='configcontext',
            name='cluster_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='virtualization.ClusterType'),
        ),
    ]
