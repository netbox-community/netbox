from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0061_fhrpgroup_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='fhrpgroupassignment',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='vlangroup',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='fhrpgroupassignment',
            constraint=models.UniqueConstraint(fields=('interface_type', 'interface_id', 'group'), name='ipam_fhrpgroupassignment_unique_interface_group'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'vid'), name='ipam_vlan_unique_group_vid'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='ipam_vlan_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(fields=('scope_type', 'scope_id', 'name'), name='ipam_vlangroup_unique_scope_name'),
        ),
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(fields=('scope_type', 'scope_id', 'slug'), name='ipam_vlangroup_unique_scope_slug'),
        ),
    ]
