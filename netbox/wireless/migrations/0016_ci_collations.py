from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'wireless_wirelesslangroup_name_2ffd60c8_like',
    'wireless_wirelesslangroup_slug_f5d59831_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0217_ci_collations'),
        ('wireless', '0015_extend_wireless_link_abs_distance_upper_limit'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='wirelesslangroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='wirelesslangroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
    ]
