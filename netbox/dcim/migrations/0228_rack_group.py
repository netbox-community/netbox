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
        # Rename any legacy dcim_rackgroup_* database objects that remain on dcim_location
        # from when the RackGroup model was renamed to Location. Old installations may have
        # retained these names, causing conflicts when the new dcim_rackgroup table is created.
        migrations.RunSQL(
            sql="""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (
                        SELECT indexname FROM pg_indexes
                        WHERE tablename = 'dcim_location' AND indexname LIKE 'dcim_rackgroup_%'
                    ) LOOP
                        EXECUTE format('ALTER INDEX %I RENAME TO %I',
                            r.indexname,
                            regexp_replace(r.indexname, '^dcim_rackgroup_', 'dcim_location_legacy_'));
                    END LOOP;

                    IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'dcim_rackgroup_id_seq' AND relkind = 'S') THEN
                        ALTER SEQUENCE dcim_rackgroup_id_seq RENAME TO dcim_location_legacy_id_seq;
                    END IF;

                    FOR r IN (
                        SELECT conname FROM pg_constraint
                        WHERE conrelid = 'dcim_location'::regclass AND conname LIKE 'dcim_rackgroup_%'
                    ) LOOP
                        EXECUTE format('ALTER TABLE dcim_location RENAME CONSTRAINT %I TO %I',
                            r.conname,
                            regexp_replace(r.conname, '^dcim_rackgroup_', 'dcim_location_legacy_'));
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
