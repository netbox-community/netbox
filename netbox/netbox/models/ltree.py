"""
Ltree-based hierarchical model support - drop-in replacement for django-mptt.

LtreeModel provides the same public API as django-mptt's MPTTModel (get_ancestors,
get_descendants, get_children, get_root, get_family, get_siblings,
get_descendant_count, get_level, level, is_root_node, is_leaf_node, is_child_node,
move_to, insert_at) backed by a PostgreSQL ltree column.

Paths are maintained entirely by PostgreSQL triggers installed via the
InstallLtreeTriggers migration operation. The Python layer never computes or
mutates paths directly; it only reads `path` back from the database after
inserts and parent_id changes via refresh_from_db(fields=['path']).
"""
from django.db import migrations, models
from django.db.models import Count, ForeignKey, Lookup, ManyToManyField, Q
from django.db.models.expressions import RawSQL

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'InstallLtreeTriggers',
    'LtreeField',
    'LtreeManager',
    'LtreeModel',
    'LtreeQuerySet',
)


#
# Field
#

class LtreeField(models.TextField):
    """
    Custom field backed by PostgreSQL's ltree type. Stores hierarchical paths
    such as "1.4.27" (each label is the integer PK of an ancestor).
    """
    description = "PostgreSQL ltree field"

    def db_type(self, connection):
        return 'ltree'

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)


@LtreeField.register_lookup
class Ancestor(Lookup):
    """`path` is an ancestor of (or equal to) the queried path:  path @> rhs"""
    lookup_name = 'ancestor'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} @> {rhs}', lhs_params + rhs_params


@LtreeField.register_lookup
class Descendant(Lookup):
    """`path` is a descendant of (or equal to) the queried path:  path <@ rhs"""
    lookup_name = 'descendant'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} <@ {rhs}', lhs_params + rhs_params


@LtreeField.register_lookup
class DescendantOrEqual(Lookup):
    """Alias of `descendant`; `<@` is inclusive in PostgreSQL ltree."""
    lookup_name = 'descendant_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} <@ {rhs}', lhs_params + rhs_params


#
# QuerySet / Manager
#

class LtreeQuerySet(RestrictedQuerySet):
    """QuerySet for ltree-based hierarchies, layered on RestrictedQuerySet."""

    def add_related_count(self, queryset, model, rel_field, count_attr, cumulative=False):
        """
        Annotate `queryset` with the count of `model` instances related via
        `rel_field`, mirroring django-mptt's `TreeManager.add_related_count`.

        When `cumulative=True`, counts include rows pointing to any descendant
        (using the ltree `<@` operator against the parent's `path`). Handles
        ForeignKey, ManyToManyField, and the NetBox GenericForeignKey "scope"
        pattern (scope_type / scope_id).
        """
        has_direct_fk = False
        is_many_to_many = False
        try:
            field = model._meta.get_field(rel_field)
            if isinstance(field, ManyToManyField):
                is_many_to_many = True
            elif isinstance(field, ForeignKey):
                has_direct_fk = True
        except Exception:
            pass

        has_generic_fk = (
            hasattr(model, 'scope_type') and hasattr(model, 'scope_id')
            and not has_direct_fk and not is_many_to_many
        )

        parent_table = queryset.model._meta.db_table
        related_table = model._meta.db_table

        if cumulative:
            if is_many_to_many:
                field = model._meta.get_field(rel_field)
                m2m_table = field.remote_field.through._meta.db_table
                # `model` is the declaring side (the side holding the items to count);
                # `queryset.model` is the related (tree) side. m2m_column_name() points
                # at the declaring model; m2m_reverse_name() points at the related model.
                m2m_to_child_col = field.m2m_column_name()
                m2m_to_tree_col = field.m2m_reverse_name()
                sql = f'''(
                    SELECT COUNT(DISTINCT "{related_table}"."id")
                    FROM "{related_table}"
                    INNER JOIN "{m2m_table}"
                      ON "{related_table}"."id" = "{m2m_table}"."{m2m_to_child_col}"
                    INNER JOIN "{parent_table}" AS subtree
                      ON "{m2m_table}"."{m2m_to_tree_col}" = subtree."id"
                    WHERE subtree."path" <@ "{parent_table}"."path"
                )'''
                return queryset.annotate(**{
                    count_attr: RawSQL(sql, [], output_field=models.IntegerField())
                })
            if has_generic_fk:
                # Resolve scope_type_id via subquery so this annotation can be
                # constructed at import time (e.g. in a view class body) even
                # before contenttypes has been migrated.
                ct_app = queryset.model._meta.app_label
                ct_model = queryset.model._meta.model_name
                sql = f'''(
                    SELECT COUNT(DISTINCT "{related_table}"."id")
                    FROM "{related_table}"
                    INNER JOIN "{parent_table}" AS subtree
                      ON "{related_table}"."scope_id" = subtree."id"
                    WHERE "{related_table}"."scope_type_id" = (
                        SELECT id FROM django_content_type
                        WHERE app_label = %s AND model = %s
                    )
                      AND subtree."path" <@ "{parent_table}"."path"
                )'''
                return queryset.annotate(**{
                    count_attr: RawSQL(sql, [ct_app, ct_model], output_field=models.IntegerField())
                })
            rel_field_col = f'{rel_field}_id'
            sql = f'''(
                    SELECT COUNT(DISTINCT "{related_table}"."id")
                    FROM "{related_table}"
                    INNER JOIN "{parent_table}" AS subtree
                      ON "{related_table}"."{rel_field_col}" = subtree."id"
                    WHERE subtree."path" <@ "{parent_table}"."path"
                )'''
            return queryset.annotate(**{
                count_attr: RawSQL(sql, [], output_field=models.IntegerField())
            })

        # Non-cumulative: direct count.
        if is_many_to_many:
            return queryset.annotate(**{count_attr: Count(rel_field, distinct=True)})
        if has_generic_fk:
            ct_app = queryset.model._meta.app_label
            ct_model = queryset.model._meta.model_name
            sql = f'''(
                SELECT COUNT(DISTINCT "{related_table}"."id")
                FROM "{related_table}"
                WHERE "{related_table}"."scope_id" = "{parent_table}"."id"
                  AND "{related_table}"."scope_type_id" = (
                      SELECT id FROM django_content_type
                      WHERE app_label = %s AND model = %s
                  )
            )'''
            return queryset.annotate(**{
                count_attr: RawSQL(sql, [ct_app, ct_model], output_field=models.IntegerField())
            })
        return queryset.annotate(**{count_attr: Count(rel_field, distinct=True)})


class LtreeManager(models.Manager.from_queryset(LtreeQuerySet)):
    """Drop-in replacement for django-mptt's TreeManager."""


#
# Abstract model
#

class LtreeModel(models.Model):
    """
    Abstract base for hierarchical models backed by PostgreSQL ltree.

    Subclasses must declare a `parent = models.ForeignKey('self', ...)`. The
    `path` column is maintained by per-table triggers installed via
    InstallLtreeTriggers; do not write to it from Python.

    Bulk creates:
        The BEFORE INSERT trigger resolves a row's parent by SELECTing
        `path` from the same table by parent_id. In a multi-row INSERT
        (e.g. `bulk_create`) PostgreSQL fires the BEFORE trigger per row in
        list order, so any row whose parent is also in the same batch
        must appear after its parent. A child placed before its parent in
        the batch will be persisted with a root-level path (the parent
        row is not yet visible to the lookup).

    Sort-path staleness:
        For subclasses with the optional `sort_path` column (see
        InstallLtreeTriggers' `name_column` arg), renaming a row does NOT
        update its sort_path — matching django-mptt's
        `order_insertion_by` behavior. Call `rebuild_sort_paths()` to
        recompute sort_path for every row from current names.
    """
    path = LtreeField(editable=False, null=False, blank=True, default='')

    objects = LtreeManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loaded_parent_id = self.parent_id

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_parent_id = instance.parent_id
        return instance

    def save(self, *args, **kwargs):
        """
        Triggers compute `path` (and `sort_path`, where present) server-side.
        After insert or after a parent change, refresh those columns so the
        in-memory instance stays consistent with the database.
        """
        is_insert = self._state.adding
        # When update_fields is supplied and excludes parent, the DB does not see
        # the new parent_id, so the trigger does not fire and _loaded_parent_id
        # must not advance — otherwise a subsequent full save() would mis-detect
        # the (real) parent change as already-applied and leave path stale.
        update_fields = kwargs.get('update_fields')
        parent_written = update_fields is None or 'parent' in update_fields or 'parent_id' in update_fields
        parent_changed = (not is_insert) and parent_written and self.parent_id != self._loaded_parent_id
        super().save(*args, **kwargs)
        if is_insert or parent_changed:
            # Refresh every trigger-maintained column (`path`, plus `sort_path` on
            # models that declare it) so the in-memory instance matches the row the
            # triggers actually wrote — otherwise e.g. change logging would snapshot
            # a stale value.
            refresh_fields = [
                name for name in ('path', 'sort_path')
                if any(f.attname == name for f in self._meta.concrete_fields)
            ]
            row = type(self).objects.values_list(*refresh_fields).get(pk=self.pk)
            for name, value in zip(refresh_fields, row):
                setattr(self, name, value)
        if is_insert or parent_written:
            self._loaded_parent_id = self.parent_id

    # -- MPTT-compatible API ------------------------------------------------

    @property
    def level(self):
        """Zero-based depth (root = 0). Mirrors django-mptt's `level`."""
        if not self.path:
            return 0
        return str(self.path).count('.')

    def get_level(self):
        return self.level

    @property
    def tree_id(self):
        """Integer PK of the root, mirroring django-mptt's `tree_id`."""
        if not self.path:
            return None
        # Strip leading zeros from the padded label
        root_label = str(self.path).split('.', 1)[0].lstrip('0') or '0'
        try:
            return int(root_label)
        except (TypeError, ValueError):
            return root_label

    def is_root_node(self):
        return self.parent_id is None

    def is_leaf_node(self):
        return not type(self).objects.filter(parent_id=self.pk).exists()

    def is_child_node(self):
        return self.parent_id is not None

    def get_root(self):
        if self.is_root_node():
            return self
        root_pk = int(str(self.path).split('.', 1)[0].lstrip('0') or '0')
        return type(self)._default_manager.get(pk=root_pk)

    def get_parent(self):
        return self.parent

    def get_ancestors(self, ascending=False, include_self=False):
        if not self.path:
            return type(self)._default_manager.none()
        qs = type(self)._default_manager.filter(path__ancestor=self.path)
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs.order_by('-path' if ascending else 'path')

    def get_descendants(self, include_self=False):
        if not self.path:
            return type(self)._default_manager.none()
        qs = type(self)._default_manager.filter(path__descendant=self.path)
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs.order_by('path')

    def get_descendant_count(self):
        if not self.path:
            return 0
        return type(self)._default_manager.filter(
            path__descendant=self.path
        ).exclude(pk=self.pk).count()

    def get_children(self):
        return type(self)._default_manager.filter(parent_id=self.pk)

    def get_family(self):
        """Ancestors + self + descendants, in path order."""
        if not self.path:
            return type(self)._default_manager.none()
        return type(self)._default_manager.filter(
            Q(path__ancestor=self.path) | Q(path__descendant=self.path)
        ).distinct().order_by('path')

    def get_siblings(self, include_self=False):
        qs = type(self)._default_manager.filter(parent_id=self.parent_id)
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs

    def move_to(self, target, position='last-child'):
        """
        Re-parent this node under `target`. Triggers handle path recomputation
        for self and all descendants. `position` is accepted for django-mptt
        compatibility; first-/last-child both mean "child of target" and
        left/right mean "sibling of target".
        """
        if position in ('first-child', 'last-child', None):
            new_parent = target
        elif position in ('left', 'right'):
            new_parent = target.parent if target else None
        else:
            raise ValueError(f"Unsupported move_to position: {position!r}")
        self.parent = new_parent
        self.save()

    def insert_at(self, target, position='last-child', save=False):
        """Set parent (optionally save). Mirrors django-mptt's insert_at."""
        if position in ('first-child', 'last-child', None):
            self.parent = target
        elif position in ('left', 'right'):
            self.parent = target.parent if target else None
        else:
            raise ValueError(f"Unsupported insert_at position: {position!r}")
        if save:
            self.save()

    @classmethod
    def rebuild_sort_paths(cls, name_column='name'):
        """
        Recompute `sort_path` for every row from current values of `name_column`.

        The BEFORE trigger updates sort_path only on INSERT and parent change,
        not on rename — matching django-mptt's `order_insertion_by` semantics.
        After renaming rows, call this to bring sort_path back in line with
        current names (and thus restore correct list ordering).

        Raises if the table does not have a `sort_path` column.
        """
        from django.db import connection

        if not any(f.name == 'sort_path' for f in cls._meta.get_fields()):
            raise NotImplementedError(
                f"{cls.__name__} does not have a sort_path column"
            )
        table = cls._meta.db_table
        sql = f'''
            WITH RECURSIVE t(id, parent_id, sort_path) AS (
                SELECT id, parent_id, "{name_column}"::text
                FROM "{table}" WHERE parent_id IS NULL
                UNION ALL
                SELECT r.id, r.parent_id, t.sort_path || chr(1) || r."{name_column}"
                FROM "{table}" r INNER JOIN t ON r.parent_id = t.id
            )
            UPDATE "{table}" SET sort_path = t.sort_path FROM t WHERE "{table}".id = t.id;
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql)


#
# Migration operation
#

# Path label is the row's PK zero-padded to 19 chars (max bigint width) so that
# lexicographic ordering of ltree labels matches numeric PK ordering across digit
# boundaries (e.g. "0...09" sorts before "0...10").
_COMPUTE_PATH_ONLY_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_compute_path_fn"() RETURNS TRIGGER AS $$
DECLARE parent_path ltree;
BEGIN
    IF NEW.parent_id IS NOT NULL THEN
        EXECUTE format('SELECT path FROM %%I WHERE id = $1', TG_TABLE_NAME)
            INTO parent_path USING NEW.parent_id;
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
    EXECUTE format(
        'UPDATE %%I SET path = $1 || subpath(path, nlevel($2))'
        ' WHERE path <@ $2 AND id != $3',
        TG_TABLE_NAME
    ) USING NEW.path, OLD.path, NEW.id;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;
'''

# For models with order_insertion_by=(name,) — maintain a second text column
# `sort_path` whose value is the chain of ancestor names joined by chr(1)
# (an unprintable separator that collates lower than any printable char in any
# standard collation). ORDER BY sort_path then gives MPTT-equivalent
# tree-flatten ordering with siblings in name (collation) order.
#
# Like MPTT's order_insertion_by, sort_path is computed at insert and
# reparent only — renaming a node does NOT reposition it. A manual rebuild()
# would be needed to re-sort everything by current names.
_COMPUTE_PATH_AND_SORT_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_compute_path_fn"() RETURNS TRIGGER AS $$
DECLARE
    parent_path ltree;
    parent_sort_path text;
BEGIN
    IF NEW.parent_id IS NOT NULL THEN
        EXECUTE format('SELECT path, sort_path FROM %%I WHERE id = $1', TG_TABLE_NAME)
            INTO parent_path, parent_sort_path USING NEW.parent_id;
        NEW.path := parent_path || lpad(NEW.id::text, 19, '0')::ltree;
        NEW.sort_path := parent_sort_path || chr(1) || NEW.{name_col};
    ELSE
        NEW.path := lpad(NEW.id::text, 19, '0')::ltree;
        NEW.sort_path := NEW.{name_col};
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
'''

_CASCADE_PATH_AND_SORT_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_cascade_path_fn"() RETURNS TRIGGER AS $$
BEGIN
    EXECUTE format(
        'UPDATE %%I SET '
        '  path = $1 || subpath(path, nlevel($2)), '
        '  sort_path = $4 || substring(sort_path FROM length($5) + 1) '
        'WHERE path <@ $2 AND id != $3',
        TG_TABLE_NAME
    ) USING NEW.path, OLD.path, NEW.id, NEW.sort_path, OLD.sort_path;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;
'''

_BEFORE_TRIGGER = '''
CREATE TRIGGER "{table}_ltree_compute_path"
    BEFORE INSERT OR UPDATE OF parent_id ON "{table}"
    FOR EACH ROW EXECUTE FUNCTION "{table}_ltree_compute_path_fn"();
'''

# Fire only on parent_id changes, not on path changes. A single reparent's
# cascade rewrites the whole subtree (WHERE path <@ OLD.path) at every depth in
# one statement, so it never needs to re-fire; including `path` here would make
# every descendant the cascade touches re-fire the trigger, each running a no-op
# cascade against its now-vacated OLD.path. Nothing mutates `path` without also
# touching `parent_id`, so `parent_id` alone is sufficient.
_AFTER_TRIGGER = '''
CREATE TRIGGER "{table}_ltree_cascade_path"
    AFTER UPDATE OF parent_id ON "{table}"
    FOR EACH ROW WHEN (OLD.path IS DISTINCT FROM NEW.path)
    EXECUTE FUNCTION "{table}_ltree_cascade_path_fn"();
'''


class InstallLtreeTriggers(migrations.operations.base.Operation):
    """
    Install per-table ltree path-maintenance triggers.

    Two row-level triggers are installed on each target table:

        BEFORE INSERT OR UPDATE OF parent_id -> compute NEW.path (and sort_path if applicable)
        AFTER UPDATE OF parent_id            -> cascade path/sort_path change to descendants

    If `name_column` is provided, the model is expected to have a `sort_path`
    text column whose value will be maintained as a chr(1)-separated chain of
    ancestor names. This implements MPTT's `order_insertion_by=(name,)`
    semantics: insert and reparent honor the current value of `name_column`;
    rename does NOT reposition the node (matching MPTT behavior).
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
        else:
            schema_editor.execute(_COMPUTE_PATH_ONLY_FN.format(table=self.table_name))
            schema_editor.execute(_CASCADE_PATH_ONLY_FN.format(table=self.table_name))
        schema_editor.execute(_BEFORE_TRIGGER.format(table=self.table_name))
        schema_editor.execute(_AFTER_TRIGGER.format(table=self.table_name))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        t = self.table_name
        schema_editor.execute(f'DROP TRIGGER IF EXISTS "{t}_ltree_cascade_path" ON "{t}";')
        schema_editor.execute(f'DROP TRIGGER IF EXISTS "{t}_ltree_compute_path" ON "{t}";')
        schema_editor.execute(f'DROP FUNCTION IF EXISTS "{t}_ltree_cascade_path_fn"();')
        schema_editor.execute(f'DROP FUNCTION IF EXISTS "{t}_ltree_compute_path_fn"();')

    def describe(self):
        return f"Install ltree path triggers on {self.table_name}"
