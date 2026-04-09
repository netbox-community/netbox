import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0229_cable_bundle'),
        ('extras', '0135_configtemplate_debug'),
        ('ipam', '0088_rename_vlangroup_total_vlan_ids'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
        ('virtualization', '0052_gfk_indexes'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('device'),
                models.F('tenant'),
                condition=models.Q(('cluster__isnull', True), ('device__isnull', False)),
                name='virtualization_virtualmachine_unique_name_device_tenant',
                violation_error_message='Virtual machine name must be unique per device and tenant.',
            ),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('device'),
                condition=models.Q(('cluster__isnull', True), ('device__isnull', False), ('tenant__isnull', True)),
                name='virtualization_virtualmachine_unique_name_device',
                violation_error_message='Virtual machine name must be unique per device.',
            ),
        ),
        migrations.AlterConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_cluster_tenant',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('cluster'),
                models.F('tenant'),
                name='virtualization_virtualmachine_unique_name_cluster_tenant',
                violation_error_message='Virtual machine name must be unique per cluster and tenant.',
            ),
        ),
    ]
