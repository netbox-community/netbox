import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0227_alter_interface_speed_bigint'),
        ('extras', '0134_owner'),
        ('users', '0015_owner'),
    ]

    operations = [
        # Rename legacy database objects left over from when the RackGroup model was renamed
        # to Location (v2.11) and Rack.group was renamed to Rack.location. Old installations
        # retained the original names, which conflict with the new dcim_rackgroup table and
        # dcim_rack.group_id column created by this migration. No-op on fresh installs.
        migrations.RunSQL(
            sql=[
                "ALTER INDEX IF EXISTS dcim_rackgroup_pkey RENAME TO dcim_location_pkey",
                "ALTER INDEX IF EXISTS dcim_rackgroup_parent_id_cc315105 RENAME TO dcim_location_parent_id_d77f3318",
                "ALTER INDEX IF EXISTS dcim_rackgroup_site_id_13520e89 RENAME TO dcim_location_site_id_b55e975f",
                "ALTER INDEX IF EXISTS dcim_rackgroup_slug_3f4582a7 RENAME TO dcim_location_slug_352c5472",
                "ALTER INDEX IF EXISTS dcim_rackgroup_slug_3f4582a7_like RENAME TO dcim_location_slug_352c5472_like",
                "ALTER INDEX IF EXISTS dcim_rackgroup_tree_id_9c2ad6f4 RENAME TO dcim_location_tree_id_5089ef14",
                "ALTER SEQUENCE IF EXISTS dcim_rackgroup_id_seq RENAME TO dcim_location_id_seq",
                # Rename the legacy index on dcim_rack from when Rack.group was renamed to
                # Rack.location. The column was renamed but the index was not, so it still
                # carries the old "group_id" name while indexing location_id. Its name
                # collides with the new index Django creates for the new Rack.group FK.
                "ALTER INDEX IF EXISTS dcim_rack_group_id_44e90ea9 RENAME TO dcim_rack_location_id_5f63ec31",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # PostgreSQL does not support IF EXISTS on RENAME CONSTRAINT, so use a DO block.
        # Target names match what a fresh v4.5.9 install produces (Django generates the FK
        # constraint name as <table>_<col>_<hash>_fk_<ref_table>_<ref_col>, where the hash is
        # md5(table + col)[:8] computed against the new dcim_location table name).
        migrations.RunSQL(
            sql="""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (
                        SELECT old_name, new_name FROM (VALUES
                            ('dcim_rackgroup_level_check', 'dcim_location_level_check'),
                            ('dcim_rackgroup_lft_check', 'dcim_location_lft_check'),
                            ('dcim_rackgroup_rght_check', 'dcim_location_rght_check'),
                            ('dcim_rackgroup_tree_id_check', 'dcim_location_tree_id_check'),
                            ('dcim_rackgroup_site_id_13520e89_fk',
                                'dcim_location_site_id_b55e975f_fk_dcim_site_id')
                        ) AS m(old_name, new_name)
                        WHERE EXISTS (
                            SELECT 1 FROM pg_constraint
                            WHERE conrelid = to_regclass('dcim_location') AND conname = m.old_name
                        )
                    ) LOOP
                        EXECUTE format('ALTER TABLE dcim_location RENAME CONSTRAINT %I TO %I',
                            r.old_name, r.new_name);
                    END LOOP;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name='RackGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                (
                    'owner',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'rack group',
                'verbose_name_plural': 'rack groups',
                'ordering': ('name',),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name='rack',
            name='group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='racks',
                to='dcim.rackgroup',
            ),
        ),
    ]
