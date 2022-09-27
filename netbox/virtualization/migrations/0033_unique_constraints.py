from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0032_virtualmachine_update_sites'),
    ]

    operations = [
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
            constraint=models.UniqueConstraint(fields=('name', 'cluster', 'tenant'), name='virtualization_virtualmachine_unique_name_cluster_tenant'),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(condition=models.Q(('tenant__isnull', True)), fields=('name', 'cluster'), name='virtualization_virtualmachine_unique_name_cluster', violation_error_message='Virtual machine name must be unique per site.'),
        ),
        migrations.AddConstraint(
            model_name='vminterface',
            constraint=models.UniqueConstraint(fields=('virtual_machine', 'name'), name='virtualization_vminterface_unique_virtual_machine_name'),
        ),
    ]
