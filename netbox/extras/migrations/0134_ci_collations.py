import django.core.validators
import re
from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'extras_configcontext_name_4bbfe25d_like',
    'extras_configcontextprofile_name_070de83b_like',
    'extras_customfield_name_2fe72707_like',
    'extras_customfieldchoiceset_name_963e63ea_like',
    'extras_customlink_name_daed2d18_like',
    'extras_eventrule_name_899453c6_like',
    'extras_notificationgroup_name_70b0a3f9_like',
    'extras_savedfilter_name_8a4bbd09_like',
    'extras_savedfilter_slug_4f93a959_like',
    'extras_tag_name_9550b3d9_like',
    'extras_tag_slug_aaa5b7e9_like',
    'extras_webhook_name_82cf60b5_like',
]


def remove_indexes(apps, schema_editor):
    for idx in PATTERN_OPS_INDEXES:
        schema_editor.execute(f'DROP INDEX IF EXISTS {idx}')


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0133_make_cf_minmax_decimal'),
        ('dcim', '0216_ci_collations'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_indexes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='configcontext',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='configcontextprofile',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='name',
            field=models.CharField(
                db_collation='ci_natural_sort',
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        message='Only alphanumeric characters and underscores are allowed.',
                        regex='^[a-z0-9_]+$',
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        inverse_match=True,
                        message='Double underscores are not permitted in custom field names.',
                        regex='__',
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='customfieldchoiceset',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='eventrule',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='notificationgroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='savedfilter',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='savedfilter',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(allow_unicode=True, db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=150, unique=True),
        ),
    ]
