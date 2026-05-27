"""Replace django-mptt with PostgreSQL ltree for wireless's hierarchical models."""
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations

import netbox.models.ltree
from netbox.models.ltree import InstallLtreeTriggers

MODEL = 'wirelesslangroup'
TABLE = 'wireless_wirelesslangroup'
LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0019_default_ordering_indexes'),
    ]

    operations = [
        # Enable the ltree extension (idempotent — CreateExtension emits IF NOT EXISTS)
        CreateExtension('ltree'),

        migrations.AddField(
            model_name=MODEL,
            name='path',
            field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
        ),

        InstallLtreeTriggers(TABLE),

        migrations.RunSQL(
            f"""
WITH RECURSIVE t(id, parent_id, path) AS (
    SELECT id, parent_id, id::text::ltree FROM "{TABLE}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id, t.path || r.id::text::ltree
    FROM "{TABLE}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{TABLE}" SET path = t.path FROM t WHERE "{TABLE}".id = t.id;
""",
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.AlterField(
            model_name=MODEL,
            name='path',
            field=netbox.models.ltree.LtreeField(blank=True, default='', editable=False),
        ),

        # Drop legacy (tree_id, lft) index added in 0018_add_mptt_tree_indexes,
        # then drop the legacy MPTT columns.
        migrations.RemoveIndex(model_name=MODEL, name='wireless_wirelesslangroup_fbcd'),
        *[migrations.RemoveField(model_name=MODEL, name=f) for f in LEGACY_FIELDS],

        migrations.AddIndex(
            model_name=MODEL,
            index=GistIndex(fields=['path'], name='wireless_lan_grp_path_gist'),
        ),
    ]
