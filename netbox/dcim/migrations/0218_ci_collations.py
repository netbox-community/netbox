from django.db import migrations, models

PATTERN_OPS_INDEXES = [
    'dcim_devicerole_slug_7952643b_like',
    'dcim_devicetype_slug_448745bd_like',
    'dcim_inventoryitemrole_name_4c8cfe6d_like',
    'dcim_inventoryitemrole_slug_3556c227_like',
    'dcim_location_slug_352c5472_like',
    'dcim_manufacturer_name_841fcd92_like',
    'dcim_manufacturer_slug_00430749_like',
    'dcim_moduletypeprofile_name_1709c36e_like',
    'dcim_platform_slug_b0908ae4_like',
    'dcim_rackrole_name_9077cfcc_like',
    'dcim_rackrole_slug_40bbcd3a_like',
    'dcim_racktype_slug_6bbb384a_like',
    'dcim_region_slug_ff078a66_like',
    'dcim_site_name_8fe66c76_like',
    'dcim_site_slug_4412c762_like',
    'dcim_sitegroup_slug_a11d2b04_like',
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
            model_name='device',
            name='dcim_device_unique_name_site_tenant',
        ),
        migrations.RemoveConstraint(
            model_name='device',
            name='dcim_device_unique_name_site',
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(blank=True, db_collation='ci_natural_sort', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='model',
            field=models.CharField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='interface',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='inventoryitemrole',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='inventoryitemrole',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='inventoryitemtemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='location',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='modulebay',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='modulebaytemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='moduletype',
            name='model',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='moduletypeprofile',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='platform',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='powerpanel',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='rack',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='racktype',
            name='model',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='racktype',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='region',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='slug',
            field=models.SlugField(db_collation='case_insensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='virtualdevicecontext',
            name='name',
            field=models.CharField(db_collation='ci_natural_sort', max_length=64),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(
                models.F('name'), models.F('site'), models.F('tenant'), name='dcim_device_unique_name_site_tenant'
            ),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(
                models.F('name'),
                models.F('site'),
                condition=models.Q(('tenant__isnull', True)),
                name='dcim_device_unique_name_site',
                violation_error_message='Device name must be unique per site.',
            ),
        ),
    ]
