from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'core_datasource_name_17788499_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_configrevision_active'),
        ('dcim', '0217_ci_collations'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='datasource',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
    ]
