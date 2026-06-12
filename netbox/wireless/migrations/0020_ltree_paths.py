"""Replace django-mptt with PostgreSQL ltree for wireless's hierarchical models.

The reverse migration is lossy: it re-adds the MPTT columns empty and does not
rebuild the tree. Forward migration is the supported direction.
"""
import django.db.models.deletion
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations, models

import netbox.models.ltree
from utilities.ltree import InstallLtreeTriggers
from utilities.mptt_to_ltree import assert_paths_populated_sql, populate_paths_sql

MODEL = 'wirelesslangroup'
TABLE = 'wireless_wirelesslangroup'
LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0019_default_ordering_indexes'),
    ]

    operations = [
        # Enable the ltree extension first so the migration fails fast if it is missing.
        CreateExtension('ltree'),

        migrations.AlterField(
            model_name='wirelesslangroup', name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='children', to='wireless.wirelesslangroup',
            ),
        ),

        migrations.AddField(
            model_name=MODEL, name='path',
            field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
        ),
        # sort_path uses natural_sort to match the WirelessLANGroup.name collation.
        migrations.AddField(
            model_name=MODEL, name='sort_path',
            field=models.TextField(
                blank=True, default='', editable=False, db_collation='natural_sort',
            ),
        ),

        InstallLtreeTriggers(TABLE, name_column='name'),

        # Populate path and sort_path for existing rows by walking the tree from
        # the roots (parent_id IS NULL) downward via a single recursive CTE.
        migrations.RunSQL(
            populate_paths_sql(TABLE, sort_path=True),
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Fail fast if any row still has NULL path (orphan FKs) before the
        # AlterField below tries to set NOT NULL inside ALTER COLUMN.
        migrations.RunSQL(
            assert_paths_populated_sql(TABLE),
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.AlterField(
            model_name=MODEL, name='path',
            field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
        ),

        migrations.AlterModelOptions(
            name=MODEL, options={'ordering': ('sort_path',)},
        ),

        migrations.RemoveIndex(model_name=MODEL, name='wireless_wirelesslangroup_fbcd'),
        *[migrations.RemoveField(model_name=MODEL, name=f) for f in LEGACY_FIELDS],

        migrations.AddIndex(
            model_name=MODEL,
            index=GistIndex(fields=['path'], name='wireless_lan_grp_path_gist'),
        ),
        migrations.AddIndex(
            model_name=MODEL,
            index=models.Index(fields=['sort_path'], name='wireless_lan_grp_sort_idx'),
        ),
    ]
