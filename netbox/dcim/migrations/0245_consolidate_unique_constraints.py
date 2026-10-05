import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0244_device__config_context_data'),
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('tenancy', '0025_ltree_paths'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
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
        # location/region/sitegroup's unique_together was rewritten from auto-named
        # constraints to these explicit names between v3.1-beta1 and v3.1.0 (0137,
        # "Fixes #7960"). Installs that ran the beta migration still have the old
        # auto-named constraints and never got these — Django's migration state only
        # tracks (app, name), not file content, so the rewrite was invisible to them.
        # Use SeparateDatabaseAndState so the DB side is a no-op on affected installs
        # (dropping constraints that were never created, plus the stale beta-era
        # leftovers under their original auto-generated names) while the migration
        # state still ends up identical to a normal install either way.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'ALTER TABLE dcim_location DROP CONSTRAINT IF EXISTS dcim_location_parent_name',
                        'ALTER TABLE dcim_location DROP CONSTRAINT IF EXISTS dcim_location_parent_slug',
                        'ALTER TABLE dcim_location '
                        'DROP CONSTRAINT IF EXISTS dcim_location_site_id_parent_id_name_5c85730c_uniq',
                        'ALTER TABLE dcim_location '
                        'DROP CONSTRAINT IF EXISTS dcim_location_site_id_parent_id_slug_4514cb1d_uniq',
                    ],
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='location',
                    name='dcim_location_parent_name',
                ),
                migrations.RemoveConstraint(
                    model_name='location',
                    name='dcim_location_parent_slug',
                ),
            ],
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
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'ALTER TABLE dcim_region DROP CONSTRAINT IF EXISTS dcim_region_parent_name',
                        'ALTER TABLE dcim_region DROP CONSTRAINT IF EXISTS dcim_region_parent_slug',
                        'ALTER TABLE dcim_region DROP CONSTRAINT IF EXISTS dcim_region_name',
                        'ALTER TABLE dcim_region DROP CONSTRAINT IF EXISTS dcim_region_slug',
                        'ALTER TABLE dcim_region '
                        'DROP CONSTRAINT IF EXISTS dcim_region_parent_id_name_2cd612fe_uniq',
                        'ALTER TABLE dcim_region '
                        'DROP CONSTRAINT IF EXISTS dcim_region_parent_id_slug_132fcac2_uniq',
                    ],
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
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
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'ALTER TABLE dcim_sitegroup DROP CONSTRAINT IF EXISTS dcim_sitegroup_parent_name',
                        'ALTER TABLE dcim_sitegroup DROP CONSTRAINT IF EXISTS dcim_sitegroup_parent_slug',
                        'ALTER TABLE dcim_sitegroup DROP CONSTRAINT IF EXISTS dcim_sitegroup_name',
                        'ALTER TABLE dcim_sitegroup DROP CONSTRAINT IF EXISTS dcim_sitegroup_slug',
                        'ALTER TABLE dcim_sitegroup '
                        'DROP CONSTRAINT IF EXISTS dcim_sitegroup_parent_id_name_ccdbb50e_uniq',
                        'ALTER TABLE dcim_sitegroup '
                        'DROP CONSTRAINT IF EXISTS dcim_sitegroup_parent_id_slug_e1b53f00_uniq',
                    ],
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
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
            ],
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
