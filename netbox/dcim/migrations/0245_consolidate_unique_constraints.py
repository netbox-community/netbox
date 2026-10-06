import django.db.models.functions.text
from django.db import migrations, models

# Installs that applied the pre-squash 0130-0159 migrations individually have
# auto-named unique constraints in place of the named ones (see #23260). Rename
# them so the RemoveConstraint operations below find what they expect.
LEGACY_CONSTRAINT_NAMES = (
    ('dcim_location', 'dcim_location_site_id_parent_id_name_5c85730c_uniq', 'dcim_location_parent_name'),
    ('dcim_location', 'dcim_location_site_id_parent_id_slug_4514cb1d_uniq', 'dcim_location_parent_slug'),
    ('dcim_region', 'dcim_region_parent_id_name_2cd612fe_uniq', 'dcim_region_parent_name'),
    ('dcim_region', 'dcim_region_parent_id_slug_132fcac2_uniq', 'dcim_region_parent_slug'),
    ('dcim_sitegroup', 'dcim_sitegroup_parent_id_name_ccdbb50e_uniq', 'dcim_sitegroup_parent_name'),
    ('dcim_sitegroup', 'dcim_sitegroup_parent_id_slug_e1b53f00_uniq', 'dcim_sitegroup_parent_slug'),
)

RENAME_LEGACY_CONSTRAINTS = '\n'.join(
    f"""
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{old}') THEN
        IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{new}') THEN
            ALTER TABLE {table} DROP CONSTRAINT {old};
        ELSE
            ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new};
        END IF;
    END IF;"""
    for table, old, new in LEGACY_CONSTRAINT_NAMES
)


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0244_device__config_context_data'),
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('tenancy', '0025_ltree_paths'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
        migrations.RunSQL(
            sql=f'DO $$ BEGIN {RENAME_LEGACY_CONSTRAINTS} END $$;',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveConstraint(
            model_name='devicerole',
            name='dcim_devicerole_parent_name',
        ),
        migrations.RemoveConstraint(
            model_name='devicerole',
            name='dcim_devicerole_name',
        ),
        migrations.RemoveConstraint(
            model_name='devicerole',
            name='dcim_devicerole_parent_slug',
        ),
        migrations.RemoveConstraint(
            model_name='devicerole',
            name='dcim_devicerole_slug',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_parent_name',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_parent_slug',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_name',
        ),
        migrations.RemoveConstraint(
            model_name='location',
            name='dcim_location_slug',
        ),
        migrations.RemoveConstraint(
            model_name='platform',
            name='dcim_platform_manufacturer_name',
        ),
        migrations.RemoveConstraint(
            model_name='platform',
            name='dcim_platform_name',
        ),
        migrations.RemoveConstraint(
            model_name='platform',
            name='dcim_platform_manufacturer_slug',
        ),
        migrations.RemoveConstraint(
            model_name='platform',
            name='dcim_platform_slug',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_parent_name',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_parent_slug',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_name',
        ),
        migrations.RemoveConstraint(
            model_name='region',
            name='dcim_region_slug',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_parent_name',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_parent_slug',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_name',
        ),
        migrations.RemoveConstraint(
            model_name='sitegroup',
            name='dcim_sitegroup_slug',
        ),
        migrations.RemoveConstraint(
            model_name='device',
            name='dcim_device_unique_name_site_tenant',
        ),
        migrations.RemoveConstraint(
            model_name='device',
            name='dcim_device_unique_name_site',
        ),
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'),
                name='dcim_devicerole_parent_name',
                nulls_distinct=False,
                violation_error_message='A device role with this name already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='dcim_devicerole_parent_slug',
                nulls_distinct=False,
                violation_error_message='A device role with this slug already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(
                fields=('site', 'parent', 'name'),
                name='dcim_location_parent_name',
                nulls_distinct=False,
                violation_error_message='A location with this name already exists within the specified site.',
            ),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(
                fields=('site', 'parent', 'slug'),
                name='dcim_location_parent_slug',
                nulls_distinct=False,
                violation_error_message='A location with this slug already exists within the specified site.',
            ),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'name'),
                name='dcim_platform_manufacturer_name',
                nulls_distinct=False,
                violation_error_message='Platform name must be unique.',
            ),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='dcim_platform_manufacturer_slug',
                nulls_distinct=False,
                violation_error_message='Platform slug must be unique.',
            ),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'),
                name='dcim_region_parent_name',
                nulls_distinct=False,
                violation_error_message='A region with this name already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='dcim_region_parent_slug',
                nulls_distinct=False,
                violation_error_message='A region with this slug already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'),
                name='dcim_sitegroup_parent_name',
                nulls_distinct=False,
                violation_error_message='A site group with this name already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='dcim_sitegroup_parent_slug',
                nulls_distinct=False,
                violation_error_message='A site group with this slug already exists.',
            ),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                models.F('site'),
                models.F('tenant'),
                condition=models.Q(('name__isnull', False)),
                name='dcim_device_unique_name_site_tenant',
                nulls_distinct=False,
                violation_error_message='Device name must be unique per site and tenant.',
            ),
        ),
    ]
