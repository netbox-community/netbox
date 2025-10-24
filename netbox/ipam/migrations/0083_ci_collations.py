from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'ipam_asnrange_name_c7585e73_like',
    'ipam_asnrange_slug_c8a7d8a1_like',
    'ipam_rir_name_64a71982_like',
    'ipam_rir_slug_ff1a369a_like',
    'ipam_role_name_13784849_like',
    'ipam_role_slug_309ca14c_like',
    'ipam_routetarget_name_212be79f_like',
    'ipam_servicetemplate_name_1a2f3410_like',
    'ipam_vlangroup_slug_40abcf6b_like',
    'ipam_vlantranslationpolicy_name_17e0a007_like',
    'ipam_vrf_rd_0ac1bde1_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0082_add_prefix_network_containment_indexes'),
        ('dcim', '0217_ci_collations'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='asnrange',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='asnrange',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='rir',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='rir',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='routetarget',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=21, unique=True),
        ),
        migrations.AlterField(
            model_name='servicetemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='vlantranslationpolicy',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='rd',
            field=models.CharField(blank=True, db_collation='case_insensitive', max_length=21, null=True, unique=True),
        ),
    ]
