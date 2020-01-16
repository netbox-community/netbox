import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('virtualization', '0002_virtualmachine_add_status'), ('virtualization', '0003_cluster_add_site'), ('virtualization', '0004_virtualmachine_add_role'), ('virtualization', '0005_django2'), ('virtualization', '0006_tags'), ('virtualization', '0007_change_logging'), ('virtualization', '0008_virtualmachine_local_context_data'), ('virtualization', '0009_custom_tag_models')]

    dependencies = [
        ('dcim', '0044_virtualization'),
        ('virtualization', '0001_virtualization'),
        ('extras', '0019_tag_taggeditem'),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[1, 'Active'], [0, 'Offline'], [3, 'Staged']], default=1, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='dcim.Site'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='role',
            field=models.ForeignKey(blank=True, limit_choices_to={'vm_role': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.DeviceRole'),
        ),
        migrations.AddField(
            model_name='clustergroup',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='clustergroup',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='clustertype',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='clustertype',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='local_context_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cluster',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
    ]
