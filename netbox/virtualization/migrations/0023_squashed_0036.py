import django.db.models.functions.text
import taggit.managers
from django.db import migrations, models

import utilities.fields
import utilities.ordering


class Migration(migrations.Migration):

    replaces = [
        ('virtualization', '0023_virtualmachine_natural_ordering'),
        ('virtualization', '0024_cluster_relax_uniqueness'),
        ('virtualization', '0025_extend_tag_support'),
        ('virtualization', '0026_vminterface_bridge'),
        ('virtualization', '0027_standardize_id_fields'),
        ('virtualization', '0028_vminterface_vrf'),
        ('virtualization', '0029_created_datetimefield'),
        ('virtualization', '0030_cluster_status'),
        ('virtualization', '0031_virtualmachine_site_device'),
        ('virtualization', '0032_virtualmachine_update_sites'),
        ('virtualization', '0033_unique_constraints'),
        ('virtualization', '0034_standardize_description_comments'),
        ('virtualization', '0035_virtualmachine_interface_count'),
        ('virtualization', '0036_virtualmachine_config_template')
    ]

    dependencies = [
        ('dcim', '0003_squashed_0130'),
        ('extras', '0098_webhook_custom_field_data_webhook_tags'),
        ('ipam', '0047_squashed_0053'),
        ('virtualization', '0022_vminterface_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='virtualmachine',
            options={'ordering': ('_name', 'pk')},
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='cluster',
            unique_together={('site', 'name'), ('group', 'name')},
        ),
        migrations.AddField(
            model_name='clustergroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='clustertype',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='vminterface',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bridge_interfaces', to='virtualization.vminterface'),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='clustergroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='clustertype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vminterface',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='vminterface',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vminterfaces', to='ipam.vrf'),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='clustergroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='clustertype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='vminterface',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cluster',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.device'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='virtualization.cluster'),
        ),
        migrations.AlterUniqueTogether(
            name='cluster',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='virtualmachine',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='vminterface',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='virtualization_cluster_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(fields=('site', 'name'), name='virtualization_cluster_unique_site_name'),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('cluster'), models.F('tenant'), name='virtualization_virtualmachine_unique_name_cluster_tenant'),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('cluster'), condition=models.Q(('tenant__isnull', True)), name='virtualization_virtualmachine_unique_name_cluster', violation_error_message='Virtual machine name must be unique per cluster.'),
        ),
        migrations.AddConstraint(
            model_name='vminterface',
            constraint=models.UniqueConstraint(fields=('virtual_machine', 'name'), name='virtualization_vminterface_unique_virtual_machine_name'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='interface_count',
            field=utilities.fields.CounterCacheField(default=0, editable=False, to_field='virtual_machine', to_model='virtualization.VMInterface'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='config_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss', to='extras.configtemplate'),
        ),
    ]
