from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'circuits_circuitgroup_name_ec8ac1e5_like',
    'circuits_circuitgroup_slug_61ca866b_like',
    'circuits_circuittype_name_8256ea9a_like',
    'circuits_circuittype_slug_9b4b3cf9_like',
    'circuits_provider_name_8f2514f5_like',
    'circuits_provider_slug_c3c0aa10_like',
    'circuits_virtualcircuittype_name_5184db16_like',
    'circuits_virtualcircuittype_slug_75d5c661_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0052_extend_circuit_abs_distance_upper_limit'),
        ('dcim', '0217_ci_collations'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='circuit',
            name='cid',
            field=models.CharField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='circuitgroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='circuitgroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='provideraccount',
            name='account',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='provideraccount',
            name='name',
            field=models.CharField(blank=True, db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='providernetwork',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='virtualcircuit',
            name='cid',
            field=models.CharField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='virtualcircuittype',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='virtualcircuittype',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
    ]
