from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'tenancy_contactgroup_slug_5b0f3e75_like',
    'tenancy_contactrole_name_44b01a1f_like',
    'tenancy_contactrole_slug_c5837d7d_like',
    'tenancy_tenant_slug_0716575e_like',
    'tenancy_tenantgroup_name_53363199_like',
    'tenancy_tenantgroup_slug_e2af1cb6_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0020_remove_contactgroupmembership'),
        ('dcim', '0216_ci_collations'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='contactgroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='contactgroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='contactrole',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='contactrole',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
    ]
