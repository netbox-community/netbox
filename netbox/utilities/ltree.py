"""
Migration support for ltree-based hierarchical models.

This module holds the schema-level machinery that backs `netbox.models.ltree`:
the PostgreSQL trigger function / trigger SQL and the `InstallLtreeTriggers`
migration operation that installs them. It is kept separate from the model layer
(`netbox.models.ltree`) so that migrations depend only on this DB-level code and
not on the model definitions.

The paths maintained by these triggers are never computed or mutated from Python;
the model layer only reads `path`/`sort_path` back from the database.
"""
from django.db import migrations

__all__ = (
    'InstallLtreeTriggers',
)


# Path label is the row's PK zero-padded to 19 chars (max bigint width) so that
# lexicographic ordering of ltree labels matches numeric PK ordering across digit
# boundaries (e.g. "0...09" sorts before "0...10").
# Per-tree advisory locking (see _lock_tree_roots_sql / LtreeModel "Concurrency"):
# every child insert / move / reparent of a node takes a transaction-level
# advisory lock keyed on the root(s) of the tree(s) it touches, BEFORE reading the
# parent path. A concurrent reparent of an ancestor takes the same key, so the two
# serialize and the AFTER cascade can never miss a row inserted concurrently;
# writes in different trees use different keys and run in parallel. Inserting a new
# root (parent_id IS NULL) takes no lock at all -- it is a race-free singleton tree
# -- so a bulk import of many top-level objects does not accumulate one lock per
# root and cannot exhaust the shared lock table.
_LOCK_TREE_ROOTS_SQL = '''
    -- A brand-new root (INSERT with parent_id IS NULL) starts its own singleton
    -- tree that no concurrent transaction can yet see (MVCC: the uncommitted row
    -- is invisible) or reference (no other transaction has its PK). For such a
    -- row this BEFORE function reads no other row (the parent lookup below is
    -- gated on parent_id) and the AFTER cascade fires only on UPDATE, so the
    -- insert touches solely its own NEW row -- there is nothing to serialize
    -- against, and the advisory lock it would otherwise take can never contend.
    -- Skipping it here is what stops a bulk import of many top-level objects from
    -- taking one xact-lock per root and exhausting the shared lock table
    -- (sized by max_locks_per_transaction). Every other case still locks below:
    -- a child insert, any reparent, and a reparent-to-root (TG_OP = UPDATE, where
    -- the existing row has a real subtree the AFTER cascade must rewrite).
    IF NOT (TG_OP = 'INSERT' AND NEW.parent_id IS NULL) THEN
        -- Destination tree root: the parent's root label, or this row's own label
        -- when it is (or becomes) a root. The CASE guards against a parent whose path
        -- is the empty ltree '' (reachable only via a trigger-bypassing raw write):
        -- subltree('', 0, 1) would raise 'invalid positions', so fall back to the
        -- child's own label as the lock key rather than aborting the insert/move.
        IF NEW.parent_id IS NOT NULL THEN
            EXECUTE format(
                'SELECT CASE WHEN nlevel(path) > 0 THEN subltree(path, 0, 1)::text END'
                ' FROM %%I WHERE id = $1',
                TG_TABLE_NAME
            ) INTO dest_root USING NEW.parent_id;
        END IF;
        dest_root := COALESCE(dest_root, lpad(NEW.id::text, 19, '0'));
        -- Source tree root (moves only): this row's current root, which the AFTER
        -- cascade will rewrite.
        IF TG_OP = 'UPDATE' AND OLD.path IS NOT NULL AND nlevel(OLD.path) > 0 THEN
            old_root := subltree(OLD.path, 0, 1)::text;
        END IF;
        key_dest := hashtextextended(TG_TABLE_NAME || ':' || dest_root, 0);
        IF old_root IS NOT NULL AND old_root <> dest_root THEN
            -- Cross-tree move: lock both roots, ascending, to avoid deadlock between
            -- two concurrent moves that touch the same pair.
            key_old := hashtextextended(TG_TABLE_NAME || ':' || old_root, 0);
            PERFORM pg_advisory_xact_lock(LEAST(key_dest, key_old));
            PERFORM pg_advisory_xact_lock(GREATEST(key_dest, key_old));
        ELSE
            PERFORM pg_advisory_xact_lock(key_dest);
        END IF;
    END IF;
'''

_COMPUTE_PATH_ONLY_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_compute_path_fn"() RETURNS TRIGGER AS $$
DECLARE
    parent_path ltree;
    dest_root text;
    old_root text;
    key_dest bigint;
    key_old bigint;
BEGIN
''' + _LOCK_TREE_ROOTS_SQL + '''
    IF NEW.parent_id IS NOT NULL THEN
        EXECUTE format('SELECT path FROM %%I WHERE id = $1', TG_TABLE_NAME)
            INTO parent_path USING NEW.parent_id;
        -- Cycle guard. The Python LtreeModel.save() also rejects cyclic moves,
        -- but a QuerySet.update() / bulk_update() bypasses save() entirely, so
        -- catch the case here as a last line of defense. A cycle exists iff
        -- this row's own label appears anywhere in parent_path (the row would
        -- become its own ancestor). Match the label as any segment via lquery.
        IF parent_path ~ ('*.' || lpad(NEW.id::text, 19, '0') || '.*')::lquery
            OR parent_path = lpad(NEW.id::text, 19, '0')::ltree THEN
            RAISE EXCEPTION 'cycle detected: %% cannot be its own ancestor', TG_TABLE_NAME
                USING ERRCODE = 'check_violation';
        END IF;
        NEW.path := parent_path || lpad(NEW.id::text, 19, '0')::ltree;
    ELSE
        NEW.path := lpad(NEW.id::text, 19, '0')::ltree;
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
'''

_CASCADE_PATH_ONLY_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_cascade_path_fn"() RETURNS TRIGGER AS $$
BEGIN
    -- `nlevel($2) > 0` guards against an empty OLD.path ('', reachable only via a
    -- trigger-bypassing raw write): `path <@ ''` is true for EVERY row, so without
    -- this the cascade would rewrite the entire table on one reparent.
    EXECUTE format(
        'UPDATE %%I SET path = $1 || subpath(path, nlevel($2))'
        ' WHERE nlevel($2) > 0 AND path <@ $2 AND id != $3',
        TG_TABLE_NAME
    ) USING NEW.path, OLD.path, NEW.id;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;
'''

# For models with order_insertion_by=(name,) — maintain a second text column
# `sort_path` whose value is the chain of ancestor names joined by chr(9) (TAB).
# TAB sorts strictly below any printable character under both the default text
# collation and the ICU `natural_sort` collation (which is `und-u-kn-true`).
# ICU collations with default variable weighting treat U+0001..U+0008 as
# variable-ignorable, so a chr(1) separator under natural_sort would interleave
# children with unrelated roots; TAB is given a primary weight and orders
# deterministically. ORDER BY sort_path then gives MPTT-equivalent
# tree-flatten ordering with siblings in name (collation) order.
#
# The BEFORE trigger fires on INSERT, parent_id changes, and name changes, so
# a rename updates the row's own sort_path; the AFTER trigger then cascades
# the new sort_path into descendants. (django-mptt's `order_insertion_by`
# stops at the renamed node and leaves descendants stale until a manual
# rebuild — NetBox auto-cascades because operators expect renames to flow
# through. `rebuild_sort_paths()` is still available for bulk repair.)
_COMPUTE_PATH_AND_SORT_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_compute_path_fn"() RETURNS TRIGGER AS $$
DECLARE
    parent_path ltree;
    parent_sort_path text;
    dest_root text;
    old_root text;
    key_dest bigint;
    key_old bigint;
BEGIN
''' + _LOCK_TREE_ROOTS_SQL + '''
    -- sort_path joins ancestor names with chr(9) (TAB); a literal tab in a name
    -- would inject a spurious separator and corrupt sibling ordering for the node
    -- and its descendants. LtreeModel.clean() rejects this for forms/serializers;
    -- this is the backstop for bulk_create / scripts / raw writes that bypass clean().
    IF position(chr(9) in COALESCE(NEW."{name_col}", '')) > 0 THEN
        RAISE EXCEPTION 'name contains a tab character, which is not allowed'
            USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.parent_id IS NOT NULL THEN
        EXECUTE format('SELECT path, sort_path FROM %%I WHERE id = $1', TG_TABLE_NAME)
            INTO parent_path, parent_sort_path USING NEW.parent_id;
        -- Cycle guard. See _COMPUTE_PATH_ONLY_FN for the rationale; this catches
        -- raw UPDATE / bulk_update paths that bypass LtreeModel.save().
        IF parent_path ~ ('*.' || lpad(NEW.id::text, 19, '0') || '.*')::lquery
            OR parent_path = lpad(NEW.id::text, 19, '0')::ltree THEN
            RAISE EXCEPTION 'cycle detected: %% cannot be its own ancestor', TG_TABLE_NAME
                USING ERRCODE = 'check_violation';
        END IF;
        NEW.path := parent_path || lpad(NEW.id::text, 19, '0')::ltree;
        NEW.sort_path := parent_sort_path || chr(9) || NEW."{name_col}";
    ELSE
        NEW.path := lpad(NEW.id::text, 19, '0')::ltree;
        NEW.sort_path := NEW."{name_col}";
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
'''

_CASCADE_PATH_AND_SORT_FN = """
CREATE OR REPLACE FUNCTION "{table}_ltree_cascade_path_fn"() RETURNS TRIGGER AS $$
BEGIN
    -- COALESCE guards against a NULL sort_path slipping in via a raw write that
    -- bypassed the BEFORE trigger: without it, length(NULL)/substring(... FROM NULL)
    -- would cascade NULL to every descendant's sort_path in one shot.
    -- `nlevel($2) > 0` guards against an empty OLD.path ('', reachable only via a
    -- trigger-bypassing raw write): `path <@ ''` is true for EVERY row, so without
    -- this the cascade would rewrite the entire table on one reparent.
    EXECUTE format(
        'UPDATE %%I SET '
        '  path = $1 || subpath(path, nlevel($2)), '
        '  sort_path = COALESCE($4, '''') || substring(COALESCE(sort_path, '''') FROM length(COALESCE($5, '''')) + 1) '
        'WHERE nlevel($2) > 0 AND path <@ $2 AND id != $3',
        TG_TABLE_NAME
    ) USING NEW.path, OLD.path, NEW.id, NEW.sort_path, OLD.sort_path;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;
"""

_BEFORE_TRIGGER_PATH_ONLY = '''
CREATE TRIGGER "{table}_ltree_compute_path"
    BEFORE INSERT OR UPDATE OF parent_id ON "{table}"
    FOR EACH ROW EXECUTE FUNCTION "{table}_ltree_compute_path_fn"();
'''

# For path+sort tables, also fire on UPDATE OF {name_col} so that renaming a
# node recomputes its sort_path. The cascade trigger then propagates the new
# sort_path to descendants.
_BEFORE_TRIGGER_PATH_AND_SORT = '''
CREATE TRIGGER "{table}_ltree_compute_path"
    BEFORE INSERT OR UPDATE OF parent_id, "{name_col}" ON "{table}"
    FOR EACH ROW EXECUTE FUNCTION "{table}_ltree_compute_path_fn"();
'''

# AFTER trigger fires on the columns that operators / Django write directly
# (parent_id and the name column) — NOT on path or sort_path. The cascade
# function rewrites path/sort_path on descendants in a single statement, and
# because that statement does not touch parent_id or {name_col}, the AFTER
# trigger does not re-fire on those descendant rows. This prevents the
# quadratic re-cascade that would otherwise occur for any deep subtree.
_AFTER_TRIGGER_PATH_ONLY = '''
CREATE TRIGGER "{table}_ltree_cascade_path"
    AFTER UPDATE OF parent_id ON "{table}"
    FOR EACH ROW WHEN (OLD.path IS DISTINCT FROM NEW.path)
    EXECUTE FUNCTION "{table}_ltree_cascade_path_fn"();
'''

_AFTER_TRIGGER_PATH_AND_SORT = '''
CREATE TRIGGER "{table}_ltree_cascade_path"
    AFTER UPDATE OF parent_id, "{name_col}" ON "{table}"
    FOR EACH ROW WHEN (
        OLD.path IS DISTINCT FROM NEW.path
        OR OLD.sort_path IS DISTINCT FROM NEW.sort_path
    )
    EXECUTE FUNCTION "{table}_ltree_cascade_path_fn"();
'''


class InstallLtreeTriggers(migrations.operations.base.Operation):
    """
    Install per-table ltree path-maintenance triggers.

    Two row-level triggers are installed on each target table:

        BEFORE INSERT OR UPDATE OF parent_id -> compute NEW.path (and sort_path if applicable)
        AFTER UPDATE OF parent_id            -> cascade path/sort_path change to descendants

    If `name_column` is provided, the model is expected to have a `sort_path`
    text column whose value will be maintained as a chr(9)-separated chain of
    ancestor names. This implements MPTT's `order_insertion_by=(name,)`
    semantics: insert, reparent, and rename all honor the current value of
    `name_column`, with renames cascaded into descendants' sort_paths.
    """
    reversible = True

    def __init__(self, table_name, name_column=None):
        self.table_name = table_name
        self.name_column = name_column

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if self.name_column:
            schema_editor.execute(_COMPUTE_PATH_AND_SORT_FN.format(
                table=self.table_name, name_col=self.name_column,
            ))
            schema_editor.execute(_CASCADE_PATH_AND_SORT_FN.format(
                table=self.table_name,
            ))
            schema_editor.execute(_BEFORE_TRIGGER_PATH_AND_SORT.format(
                table=self.table_name, name_col=self.name_column,
            ))
            schema_editor.execute(_AFTER_TRIGGER_PATH_AND_SORT.format(
                table=self.table_name, name_col=self.name_column,
            ))
        else:
            schema_editor.execute(_COMPUTE_PATH_ONLY_FN.format(table=self.table_name))
            schema_editor.execute(_CASCADE_PATH_ONLY_FN.format(table=self.table_name))
            schema_editor.execute(_BEFORE_TRIGGER_PATH_ONLY.format(table=self.table_name))
            schema_editor.execute(_AFTER_TRIGGER_PATH_ONLY.format(table=self.table_name))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        t = self.table_name
        schema_editor.execute(f'DROP TRIGGER IF EXISTS "{t}_ltree_cascade_path" ON "{t}";')
        schema_editor.execute(f'DROP TRIGGER IF EXISTS "{t}_ltree_compute_path" ON "{t}";')
        schema_editor.execute(f'DROP FUNCTION IF EXISTS "{t}_ltree_cascade_path_fn"();')
        schema_editor.execute(f'DROP FUNCTION IF EXISTS "{t}_ltree_compute_path_fn"();')

    def describe(self):
        return f"Install ltree path triggers on {self.table_name}"
