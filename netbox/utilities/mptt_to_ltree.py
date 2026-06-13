"""
Reusable SQL builders for migrating a django-mptt tree to a PostgreSQL ltree
`path` (and optional `sort_path`) column.

NetBox's core hierarchical models moved from django-mptt to ltree in v4.6. The
per-table data backfill that migration performs is identical in shape for every
tree, so the SQL is centralized here rather than copied into each app's
migration. This also gives plugin maintainers a supported path for migrating
their own MPTT models to `netbox.models.ltree.LtreeModel`; from a data migration:

    from django.contrib.postgres.operations import CreateExtension
    from django.db import migrations
    from utilities.ltree import InstallLtreeTriggers
    from utilities.mptt_to_ltree import assert_paths_populated_sql, populate_paths_sql

    operations = [
        CreateExtension('ltree'),
        # ... AddField('path', nullable), [AddField('sort_path')], InstallLtreeTriggers(...) ...
        migrations.RunSQL(
            populate_paths_sql('myplugin_mymodel', sort_path=True),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            assert_paths_populated_sql('myplugin_mymodel'),
            reverse_sql=migrations.RunSQL.noop,
        ),
        # ... AlterField('path' -> NOT NULL) ...
    ]

The values produced here must stay byte-identical to what the runtime triggers
in `utilities.ltree` maintain: each path label is the row PK zero-padded to
`_PATH_LABEL_WIDTH` chars, and `sort_path` is the chr(9) (TAB) separated chain of
ancestor `name` values. Keep the two modules in sync if either changes.
"""

__all__ = (
    'assert_paths_populated_sql',
    'populate_paths_sql',
)

# Width to which each PK is zero-padded when used as an ltree label. Must match
# the lpad() width used by the trigger functions in utilities.ltree (19 = max
# bigint digit width) so that backfilled paths and trigger-maintained paths sort
# and compare identically.
_PATH_LABEL_WIDTH = 19


def populate_paths_sql(table, *, sort_path=False):
    """
    Return SQL that backfills `path` (and `sort_path` when `sort_path=True`) for
    every existing row in `table`, walking the tree from its roots
    (parent_id IS NULL) downward via a single recursive CTE.

    `path` is the chain of PK labels, each zero-padded to `_PATH_LABEL_WIDTH`
    chars. `sort_path` is the chr(9) (TAB) separated chain of ancestor `name`
    values, matching the `order_insertion_by=('name',)` semantics the triggers
    maintain at runtime.

    !!! warning
        The UPDATE takes a row-exclusive lock on the entire table for the
        duration of the statement. On large tables this can block writes for
        minutes — plan a maintenance window accordingly.
    """
    if sort_path:
        return f"""
WITH RECURSIVE t(id, parent_id, path, sort_path) AS (
    SELECT id, parent_id,
           lpad(id::text, {_PATH_LABEL_WIDTH}, '0')::ltree,
           name::text
    FROM "{table}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id,
           t.path || lpad(r.id::text, {_PATH_LABEL_WIDTH}, '0')::ltree,
           t.sort_path || chr(9) || r.name
    FROM "{table}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{table}" SET path = t.path, sort_path = t.sort_path
FROM t WHERE "{table}".id = t.id;
"""
    return f"""
WITH RECURSIVE t(id, parent_id, path) AS (
    SELECT id, parent_id, lpad(id::text, {_PATH_LABEL_WIDTH}, '0')::ltree
    FROM "{table}" WHERE parent_id IS NULL
    UNION ALL
    SELECT r.id, r.parent_id, t.path || lpad(r.id::text, {_PATH_LABEL_WIDTH}, '0')::ltree
    FROM "{table}" r JOIN t ON r.parent_id = t.id
)
UPDATE "{table}" SET path = t.path FROM t WHERE "{table}".id = t.id;
"""


def assert_paths_populated_sql(table):
    """
    Return SQL that raises if any row in `table` still has a NULL `path` after
    `populate_paths_sql()` runs.

    The recursive CTE only reaches rows whose ancestry chains back to a
    `parent_id IS NULL` root, so any row left with a NULL path points (directly
    or transitively) at an orphan or cyclic parent_id. Catch that here, naming
    the table and row count, rather than letting the subsequent
    `AlterField(path -> NOT NULL)` abort opaquely inside ALTER COLUMN.
    """
    return f"""
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
"""
