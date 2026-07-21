import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0243_consolidate_unique_constraints'),
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('ipam', '0094_denormalization_triggers'),
        ('tenancy', '0026_consolidate_unique_constraints'),
        ('users', '0016_default_ordering_indexes'),
        ('virtualization', '0059_virtualmachine__config_context_data'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_cluster_tenant',
        ),
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_cluster',
        ),
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_device_tenant',
        ),
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_device',
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('cluster'),
                models.F('tenant'),
                condition=models.Q(('cluster__isnull', False)),
                name='virtualization_virtualmachine_unique_name_cluster_tenant',
                nulls_distinct=False,
                violation_error_message='Virtual machine name must be unique per cluster and tenant.',
            ),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('device'),
                models.F('tenant'),
                condition=models.Q(('cluster__isnull', True), ('device__isnull', False)),
                name='virtualization_virtualmachine_unique_name_device_tenant',
                nulls_distinct=False,
                violation_error_message='Virtual machine name must be unique per device and tenant.',
            ),
        ),
    ]
