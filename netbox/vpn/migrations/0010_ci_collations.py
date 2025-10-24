from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'vpn_ikepolicy_name_5124aa3b_like',
    'vpn_ikeproposal_name_254623b7_like',
    'vpn_ipsecpolicy_name_cf28a1aa_like',
    'vpn_ipsecprofile_name_3ac63c72_like',
    'vpn_ipsecproposal_name_2fb98e2b_like',
    'vpn_l2vpn_name_8824eda5_like',
    'vpn_l2vpn_slug_76b5a174_like',
    'vpn_tunnel_name_f060beab_like',
    'vpn_tunnelgroup_name_9f6ebf92_like',
    'vpn_tunnelgroup_slug_9e614d62_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0217_ci_collations'),
        ('vpn', '0009_remove_redundant_indexes'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='ikepolicy',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ikeproposal',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecpolicy',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecprofile',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecproposal',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='l2vpn',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='l2vpn',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tunnel',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tunnelgroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tunnelgroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
    ]
