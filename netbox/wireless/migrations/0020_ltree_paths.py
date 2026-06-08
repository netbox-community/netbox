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

MODEL = 'wirelesslangroup'
TABLE = 'wireless_wirelesslangroup'
LEGACY_FIELDS = ('lft', 'rght', 'tree_id', 'level')


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0019_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslangroup', name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='children', to='wireless.wirelesslangroup',
            ),
        ),

        CreateExtension('ltree'),

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

        migrations.RunSQL(
            f"""
WITH RECURSIVE t(id, parent_id, path, sort_path) AS (
    SELECT id, parent_id,
           lpad(id::text, 19, '0')::ltree,
           name::text
    FROM "{TABLE}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id,
           t.path || lpad(r.id::text, 19, '0')::ltree,
           t.sort_path || chr(9) || r.name
    FROM "{TABLE}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{TABLE}" SET path = t.path, sort_path = t.sort_path
FROM t WHERE "{TABLE}".id = t.id;
""",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Fail fast if any row still has NULL path (orphan FKs) before the
        # AlterField below tries to set NOT NULL inside ALTER COLUMN.
        migrations.RunSQL(
            f"""
DO $$
DECLARE missing bigint;
BEGIN
    SELECT count(*) INTO missing FROM "{TABLE}" WHERE path IS NULL;
    IF missing > 0 THEN
        RAISE EXCEPTION
            'ltree backfill left % rows in "{TABLE}" with NULL path; '
            'likely orphan parent_id references — resolve before re-running '
            'this migration', missing;
    END IF;
END $$;
""",
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
