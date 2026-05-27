"""Replace django-mptt with PostgreSQL ltree for tenancy's hierarchical models."""
from django.contrib.postgres.indexes import GistIndex
from django.db import migrations

import netbox.models.ltree
from netbox.models.ltree import InstallLtreeTriggers

MODELS = ('tenantgroup', 'contactgroup')
TABLES = ('tenancy_tenantgroup', 'tenancy_contactgroup')
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
        ('tenancy', '0025_enable_ltree_extension'),
    ]

    operations = [
        *[
            migrations.AddField(
                model_name=m,
                name='path',
                field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
            )
            for m in MODELS
        ],

        *[InstallLtreeTriggers(t) for t in TABLES],

        migrations.RunSQL(_populate_paths_sql(), reverse_sql=migrations.RunSQL.noop),

        *[
            migrations.AlterField(
                model_name=m,
                name='path',
                field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
            )
            for m in MODELS
        ],

        # Drop legacy (tree_id, lft) indexes added in 0023_add_mptt_tree_indexes,
        # then drop the legacy MPTT columns.
        migrations.RemoveIndex(model_name='contactgroup', name='tenancy_contactgroup_tree_d2ce'),
        migrations.RemoveIndex(model_name='tenantgroup', name='tenancy_tenantgroup_tree_ifebc'),
        *[
            migrations.RemoveField(model_name=m, name=f)
            for m in MODELS for f in LEGACY_FIELDS
        ],

        migrations.AddIndex(
            model_name='tenantgroup',
            index=GistIndex(fields=['path'], name='tenancy_tenantgroup_path_gist'),
        ),
        migrations.AddIndex(
            model_name='contactgroup',
            index=GistIndex(fields=['path'], name='tenancy_contactgroup_path_gist'),
        ),
    ]
