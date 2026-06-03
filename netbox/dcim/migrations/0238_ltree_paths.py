"""
Replace django-mptt with PostgreSQL ltree for dcim's hierarchical models.

For each of (Region, SiteGroup, Location, DeviceRole, Platform, ModuleBay,
InventoryItem, InventoryItemTemplate) this migration:

1. Enables the PostgreSQL ltree extension (idempotent).
2. Adds a nullable `path` LTreeField. For models that previously had
   `MPTTMeta.order_insertion_by = ('name',)` — Region, SiteGroup, Location,
   DeviceRole, Platform, ModuleBay — also adds a `sort_path` text column.
3. Installs per-table BEFORE/AFTER triggers. For models with sort_path, the
   trigger maintains both columns.
4. Populates path (and sort_path where applicable) for existing rows via a
   single recursive CTE per table.
5. Tightens path to NOT NULL.
6. Drops the legacy MPTT columns (lft, rght, tree_id, level).
7. Adds a GiST index on path (descendant/ancestor lookups via `<@` / `@>`).
   For sort_path models, also adds a btree index for ORDER BY listing.

!!! OPERATOR WARNING !!!

Step 4 runs ONE recursive-CTE UPDATE per table over every row, taking a
row-exclusive lock on the entire table for the duration of the statement.
On large deployments — particularly dcim_inventoryitem, which can contain
millions of rows — this can block writes for minutes. Plan a maintenance
window and budget accordingly. The other tables (region, sitegroup,
location, devicerole, platform, modulebay, inventoryitemtemplate) are
typically far smaller.

Notes:
- The reverse migration is lossy: it re-adds the MPTT columns (lft/rght/tree_id/
  level) empty and does NOT rebuild the tree. Forward migration is the supported
  direction.
"""
import django.db.models.deletion
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations, models

import netbox.models.ltree
from netbox.models.ltree import InstallLtreeTriggers

# All models getting an ltree `path` column.
ALL_MODELS = (
    'region', 'sitegroup', 'location', 'devicerole', 'platform',
    'inventoryitem', 'inventoryitemtemplate', 'modulebay',
)

ALL_TABLES = (
    'dcim_region',
    'dcim_sitegroup',
    'dcim_location',
    'dcim_devicerole',
    'dcim_platform',
    'dcim_inventoryitem',
    'dcim_inventoryitemtemplate',
    'dcim_modulebay',
)

# Subset that previously declared `MPTTMeta.order_insertion_by = ('name',)` and
# therefore needs a `sort_path` text column maintained alongside `path`.
SORT_MODELS = ('region', 'sitegroup', 'location', 'devicerole', 'platform', 'modulebay')

SORT_TABLES = (
    'dcim_region',
    'dcim_sitegroup',
    'dcim_location',
    'dcim_devicerole',
    'dcim_platform',
    'dcim_modulebay',
)

LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


def _populate_paths_sql():
    """
    Build the recursive CTE that walks each table from roots downward, computing
    the new path (PK-based, zero-padded) and — for models with sort_path — the
    chr(9)-separated chain of ancestor names.
    """
    blocks = []
    for table in ALL_TABLES:
        if table in SORT_TABLES:
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
        else:
            blocks.append(f"""
WITH RECURSIVE t(id, parent_id, path) AS (
    SELECT id, parent_id, lpad(id::text, 19, '0')::ltree FROM "{table}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id, t.path || lpad(r.id::text, 19, '0')::ltree
    FROM "{table}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{table}" SET path = t.path FROM t WHERE "{table}".id = t.id;
""")
    return '\n'.join(blocks)


def _assert_paths_populated_sql():
    """
    After the recursive CTE backfills paths from `parent_id IS NULL` roots, any
    row whose parent_id points to a row that the CTE could not reach (orphan FK,
    stray cycle left by a prior raw write) will still have path IS NULL. The
    immediately following AlterField that sets path to NOT NULL would then abort
    inside ALTER COLUMN with an opaque message. Fail fast here instead so the
    operator sees the offending table and row counts.
    """
    checks = []
    for table in ALL_TABLES:
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
        ('dcim', '0237_module_remove_local_context_data'),
    ]

    operations = [
        # Switch parent from mptt.fields.TreeForeignKey to django.db.models.ForeignKey
        # (no-op at the SQL level; reconciles migration state with model definitions).
        migrations.AlterField(
            model_name='devicerole', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.devicerole'),
        ),
        migrations.AlterField(
            model_name='inventoryitem', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='child_items', to='dcim.inventoryitem'),
        ),
        migrations.AlterField(
            model_name='inventoryitemtemplate', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='child_items', to='dcim.inventoryitemtemplate'),
        ),
        migrations.AlterField(
            model_name='location', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.location'),
        ),
        migrations.AlterField(
            model_name='modulebay', name='parent',
            field=models.ForeignKey(blank=True, editable=False, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.modulebay'),
        ),
        migrations.AlterField(
            model_name='platform', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.platform'),
        ),
        migrations.AlterField(
            model_name='region', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.region'),
        ),
        migrations.AlterField(
            model_name='sitegroup', name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='children', to='dcim.sitegroup'),
        ),

        # 1. Enable the ltree extension (idempotent).
        CreateExtension('ltree'),

        # 2. Add nullable path column on all tree models.
        *[
            migrations.AddField(
                model_name=m, name='path',
                field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
            )
            for m in ALL_MODELS
        ],
        # 2b. Add sort_path column (with default '') on the 6 models with order_insertion_by.
        #     ModuleBay's `name` uses the natural_sort collation, so its sort_path must
        #     match it (Slot 0..Slot 13, not lexicographic Slot 0, 1, 10, 2...). The other
        #     five use a plain-collation `name`, so their sort_path stays plain.
        *[
            migrations.AddField(
                model_name=m, name='sort_path',
                field=models.TextField(blank=True, default='', editable=False),
            )
            for m in SORT_MODELS if m != 'modulebay'
        ],
        migrations.AddField(
            model_name='modulebay', name='sort_path',
            field=models.TextField(blank=True, default='', editable=False, db_collation='natural_sort'),
        ),

        # 3. Install path-maintenance triggers. Models with sort_path get triggers
        #    that maintain both columns; the other two get path-only triggers.
        *[InstallLtreeTriggers(t, name_column='name') for t in SORT_TABLES],
        InstallLtreeTriggers('dcim_inventoryitem'),
        InstallLtreeTriggers('dcim_inventoryitemtemplate'),

        # 4. Populate existing rows via per-table recursive CTE.
        migrations.RunSQL(_populate_paths_sql(), reverse_sql=migrations.RunSQL.noop),

        # 4b. Fail fast (with a useful message) if any row still has NULL path —
        #     otherwise the AlterField below aborts opaquely inside ALTER COLUMN.
        migrations.RunSQL(_assert_paths_populated_sql(), reverse_sql=migrations.RunSQL.noop),

        # 5. Tighten path to NOT NULL with empty-string default.
        *[
            migrations.AlterField(
                model_name=m, name='path',
                field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
            )
            for m in ALL_MODELS
        ],

        # 6. Update Meta.ordering on the SORT_MODELS to reflect sort_path-based ordering.
        migrations.AlterModelOptions(
            name='devicerole', options={'ordering': ('sort_path',)},
        ),
        migrations.AlterModelOptions(
            name='location', options={'ordering': ('site', 'sort_path')},
        ),
        migrations.AlterModelOptions(
            name='modulebay', options={'ordering': ('device', 'sort_path')},
        ),
        migrations.AlterModelOptions(
            name='platform', options={'ordering': ('sort_path',)},
        ),
        migrations.AlterModelOptions(
            name='region', options={'ordering': ('sort_path',)},
        ),
        migrations.AlterModelOptions(
            name='sitegroup', options={'ordering': ('sort_path',)},
        ),

        # 7. Drop legacy (tree_id, lft) indexes added in 0226_add_mptt_tree_indexes,
        # then drop the legacy MPTT columns.
        migrations.RemoveIndex(model_name='devicerole', name='dcim_devicerole_tree_id_lfbf11'),
        migrations.RemoveIndex(model_name='inventoryitem', name='dcim_inventoryitem_tree_id975c'),
        migrations.RemoveIndex(model_name='inventoryitemtemplate', name='dcim_inventoryitemtemplatedee0'),
        migrations.RemoveIndex(model_name='location', name='dcim_location_tree_id_lft_idx'),
        migrations.RemoveIndex(model_name='modulebay', name='dcim_modulebay_tree_id_lft_idx'),
        migrations.RemoveIndex(model_name='platform', name='dcim_platform_tree_id_lft_idx'),
        migrations.RemoveIndex(model_name='region', name='dcim_region_tree_id_lft_idx'),
        migrations.RemoveIndex(model_name='sitegroup', name='dcim_sitegroup_tree_id_lft_idx'),
        *[
            migrations.RemoveField(model_name=m, name=f)
            for m in ALL_MODELS for f in LEGACY_FIELDS
        ],

        # 8. Add GiST indexes on path (descendant/ancestor containment).
        migrations.AddIndex(
            model_name='region',
            index=GistIndex(fields=['path'], name='dcim_region_path_gist'),
        ),
        migrations.AddIndex(
            model_name='sitegroup',
            index=GistIndex(fields=['path'], name='dcim_sitegroup_path_gist'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=GistIndex(fields=['path'], name='dcim_location_path_gist'),
        ),
        migrations.AddIndex(
            model_name='devicerole',
            index=GistIndex(fields=['path'], name='dcim_devicerole_path_gist'),
        ),
        migrations.AddIndex(
            model_name='platform',
            index=GistIndex(fields=['path'], name='dcim_platform_path_gist'),
        ),
        migrations.AddIndex(
            model_name='inventoryitem',
            index=GistIndex(fields=['path'], name='dcim_inventoryitem_path_gist'),
        ),
        migrations.AddIndex(
            model_name='inventoryitemtemplate',
            index=GistIndex(fields=['path'], name='dcim_inv_item_tmpl_path_gist'),
        ),
        migrations.AddIndex(
            model_name='modulebay',
            index=GistIndex(fields=['path'], name='dcim_modulebay_path_gist'),
        ),

        # 9. Add btree indexes on sort_path (tree-flatten ORDER BY listing).
        migrations.AddIndex(
            model_name='region',
            index=models.Index(fields=['sort_path'], name='dcim_region_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='sitegroup',
            index=models.Index(fields=['sort_path'], name='dcim_sitegroup_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['sort_path'], name='dcim_location_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='devicerole',
            index=models.Index(fields=['sort_path'], name='dcim_devicerole_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='platform',
            index=models.Index(fields=['sort_path'], name='dcim_platform_sort_path_idx'),
        ),
        migrations.AddIndex(
            model_name='modulebay',
            index=models.Index(fields=['sort_path'], name='dcim_modulebay_sort_path_idx'),
        ),
    ]
