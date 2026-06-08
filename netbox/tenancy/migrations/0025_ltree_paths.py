"""Replace django-mptt with PostgreSQL ltree for tenancy's hierarchical models.

The reverse migration is lossy: it re-adds the MPTT columns empty and does not
rebuild the tree. Forward migration is the supported direction.
"""
import django.db.models.deletion
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations, models

import netbox.models.ltree
from utilities.ltree import InstallLtreeTriggers

MODELS = ('tenantgroup', 'contactgroup')
TABLES = ('tenancy_tenantgroup', 'tenancy_contactgroup')
LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


def _populate_paths_sql():
    blocks = []
    for table in TABLES:
        blocks.append(f"""
WITH RECURSIVE t(id, parent_id, path, sort_path) AS (
    SELECT id, parent_id,
           lpad(id::text, 19, '0')::ltree,
           name::text
    FROM "{table}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id,
           t.path || lpad(r.id::text, 19, '0')::ltree,
           t.sort_path || chr(9) || r.name
    FROM "{table}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{table}" SET path = t.path, sort_path = t.sort_path
FROM t WHERE "{table}".id = t.id;
""")
    return '\n'.join(blocks)


def _assert_paths_populated_sql():
    checks = []
    for table in TABLES:
        checks.append(f"""
DO $$
DECLARE missing bigint;
BEGIN
    SELECT count(*) INTO missing FROM "{table}" WHERE path IS NULL;
    IF missing > 0 THEN
        RAISE EXCEPTION
            'ltree backfill left % rows in "{table}" with NULL path; '
            'likely orphan parent_id references — resolve before re-running '
            'this migration', missing;
    END IF;
END $$;
""")
    return '\n'.join(checks)


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0024_default_ordering_indexes'),
    ]

    operations = [
        # Switch parent from mptt.fields.TreeForeignKey to django.db.models.ForeignKey.
        migrations.AlterField(
            model_name='contactgroup', name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='children', to='tenancy.contactgroup',
            ),
        ),
        migrations.AlterField(
            model_name='tenantgroup', name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='children', to='tenancy.tenantgroup',
            ),
        ),

        CreateExtension('ltree'),

        # Add path (nullable initially) on both models.
        *[
            migrations.AddField(
                model_name=m, name='path',
                field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
            )
            for m in MODELS
        ],
        # Add sort_path. TenantGroup gets natural_sort collation (matching its name field).
        migrations.AddField(
            model_name='contactgroup', name='sort_path',
            field=models.TextField(blank=True, default='', editable=False),
        ),
        migrations.AddField(
            model_name='tenantgroup', name='sort_path',
            field=models.TextField(
                blank=True, default='', editable=False, db_collation='natural_sort',
            ),
        ),

        # Install triggers maintaining both path and sort_path.
        *[InstallLtreeTriggers(t, name_column='name') for t in TABLES],

        migrations.RunSQL(_populate_paths_sql(), reverse_sql=migrations.RunSQL.noop),

        # Fail fast if any row still has NULL path (orphan FKs) before the
        # AlterField below tries to set NOT NULL inside ALTER COLUMN.
        migrations.RunSQL(_assert_paths_populated_sql(), reverse_sql=migrations.RunSQL.noop),

        *[
            migrations.AlterField(
                model_name=m, name='path',
                field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
            )
            for m in MODELS
        ],

        migrations.AlterModelOptions(
            name='contactgroup', options={'ordering': ('sort_path',)},
        ),
        migrations.AlterModelOptions(
            name='tenantgroup', options={'ordering': ('sort_path',)},
        ),

        # Drop legacy (tree_id, lft) indexes and the MPTT columns.
        migrations.RemoveIndex(model_name='contactgroup', name='tenancy_contactgroup_tree_d2ce'),
        migrations.RemoveIndex(model_name='tenantgroup', name='tenancy_tenantgroup_tree_ifebc'),
        *[
            migrations.RemoveField(model_name=m, name=f)
            for m in MODELS for f in LEGACY_FIELDS
        ],

        # GiST indexes on path.
        migrations.AddIndex(
            model_name='tenantgroup',
            index=GistIndex(fields=['path'], name='tenancy_tenantgroup_path_gist'),
        ),
        migrations.AddIndex(
            model_name='contactgroup',
            index=GistIndex(fields=['path'], name='tenancy_contactgroup_path_gist'),
        ),

        # Btree indexes on sort_path for ORDER BY listing.
        migrations.AddIndex(
            model_name='tenantgroup',
            index=models.Index(fields=['sort_path'], name='tenancy_tg_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='contactgroup',
            index=models.Index(fields=['sort_path'], name='tenancy_cg_sort_path_idx'),
        ),
    ]
