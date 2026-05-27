"""
Replace django-mptt with PostgreSQL ltree for dcim's hierarchical models.

For each of (Region, SiteGroup, Location, DeviceRole, Platform, ModuleBay,
InventoryItem, InventoryItemTemplate) this migration:

1. Enables the PostgreSQL ltree extension (idempotent).
2. Adds a nullable `path` LTreeField.
3. Installs per-table BEFORE-INSERT/UPDATE-OF-parent_id and AFTER-UPDATE-OF-(parent_id, path)
   triggers so concurrent writes during the long-running data step get correct paths.
4. Populates paths for existing rows via a single recursive CTE per table.
5. Tightens `path` to NOT NULL.
6. Drops the legacy MPTT columns (lft, rght, tree_id, level).
7. Adds a GiST index on the `path` column for efficient `@>` / `<@` lookups.
"""
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations

import netbox.models.ltree
from netbox.models.ltree import InstallLtreeTriggers

MODELS = (
    'region', 'sitegroup', 'location', 'devicerole', 'platform',
    'inventoryitem', 'inventoryitemtemplate', 'modulebay',
)

TABLES = (
    'dcim_region',
    'dcim_sitegroup',
    'dcim_location',
    'dcim_devicerole',
    'dcim_platform',
    'dcim_inventoryitem',
    'dcim_inventoryitemtemplate',
    'dcim_modulebay',
)

LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


def _populate_paths_sql():
    blocks = []
    for table in TABLES:
        blocks.append(f"""
WITH RECURSIVE t(id, parent_id, path) AS (
    SELECT id, parent_id, id::text::ltree FROM "{table}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id, t.path || r.id::text::ltree
    FROM "{table}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{table}" SET path = t.path FROM t WHERE "{table}".id = t.id;
""")
    return '\n'.join(blocks)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0233_device_render_config_permission'),
    ]

    operations = [
        # 1. Enable the ltree extension (idempotent — CreateExtension emits IF NOT EXISTS)
        CreateExtension('ltree'),

        # 2. Add nullable path column
        *[
            migrations.AddField(
                model_name=m,
                name='path',
                field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
            )
            for m in MODELS
        ],

        # 2. Install path-maintenance triggers
        *[InstallLtreeTriggers(t) for t in TABLES],

        # 3. Populate existing rows
        migrations.RunSQL(_populate_paths_sql(), reverse_sql=migrations.RunSQL.noop),

        # 4. Tighten to NOT NULL with empty-string default
        *[
            migrations.AlterField(
                model_name=m,
                name='path',
                field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
            )
            for m in MODELS
        ],

        # 5. Drop legacy (tree_id, lft) indexes added in 0226_add_mptt_tree_indexes,
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
            for m in MODELS for f in LEGACY_FIELDS
        ],

        # 6. Add GiST indexes on path
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
    ]
