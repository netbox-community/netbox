from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'virtualization_clustergroup_name_4fcd26b4_like',
    'virtualization_clustergroup_slug_57ca1d23_like',
    'virtualization_clustertype_name_ea854d3d_like',
    'virtualization_clustertype_slug_8ee4d0e0_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0217_ci_collations'),
        ('extras', '0134_ci_collations'),
        ('ipam', '0083_ci_collations'),
        ('tenancy', '0021_ci_collations'),
        ('virtualization', '0048_populate_mac_addresses'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_cluster_tenant',
        ),
        migrations.RemoveConstraint(
            model_name='virtualmachine',
            name='virtualization_virtualmachine_unique_name_cluster',
        ),
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='clustergroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='clustergroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='clustertype',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='clustertype',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='virtualdisk',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                models.F('name'),
                models.F('cluster'),
                models.F('tenant'),
                name='virtualization_virtualmachine_unique_name_cluster_tenant',
            ),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(
                models.F('name'),
                models.F('cluster'),
                condition=models.Q(('tenant__isnull', True)),
                name='virtualization_virtualmachine_unique_name_cluster',
                violation_error_message='Virtual machine name must be unique per cluster.',
            ),
        ),
    ]
