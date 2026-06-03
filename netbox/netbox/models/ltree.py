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
from django.core.exceptions import ValidationError
from django.db import connection, migrations, models
from django.db.models import ForeignKey, Lookup, ManyToManyField, Q
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'InstallLtreeTriggers',
    'LtreeField',
    'LtreeManager',
    'LtreeModel',
    'LtreeQuerySet',
    'SortPathField',
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

    # `path` is computed by a BEFORE INSERT trigger, so its final value isn't known
    # until the row is written. Marking the field db_returning lets the
    # INSERT ... RETURNING clause fetch the trigger-computed value in the same
    # round-trip (PostgreSQL evaluates RETURNING after BEFORE triggers fire),
    # avoiding a follow-up SELECT in LtreeModel.save(). Mirrors AutoFieldMixin.
    db_returning = True

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
    """
    `path` is a strict descendant of the queried path:  path <@ rhs AND path <> rhs.

    Use `descendant_or_equal` for the inclusive form (`<@`).
    """
    lookup_name = 'descendant'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'({lhs} <@ {rhs} AND {lhs} <> {rhs})', lhs_params + rhs_params + lhs_params + rhs_params


@LtreeField.register_lookup
class DescendantOrEqual(Lookup):
    """`path` is a descendant of (or equal to) the queried path:  path <@ rhs"""
    lookup_name = 'descendant_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} <@ {rhs}', lhs_params + rhs_params


class SortPathField(models.TextField):
    """
    Text column holding the chr(9)-separated chain of ancestor names that drives
    tree-flatten ordering. Like `path`, its value is maintained by triggers, so it
    is marked db_returning to be populated via INSERT ... RETURNING without an
    extra SELECT. It deconstructs as a plain TextField so existing migrations
    (which created the column as TextField) require no schema change.
    """
    db_returning = True

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, 'django.db.models.TextField', args, kwargs


#
# QuerySet / Manager
#

class LtreeQuerySet(RestrictedQuerySet):
    """QuerySet for ltree-based hierarchies, layered on RestrictedQuerySet."""

    def bulk_create(self, objs, *args, **kwargs):
        """
        Same as the standard `bulk_create` but verifies that, for every row whose
        parent is an unsaved instance, the parent appears earlier in the same
        batch. PostgreSQL fires the BEFORE INSERT trigger per row in list order;
        a child whose parent is unsaved and either (a) appears later in the batch
        or (b) is not in the batch at all would otherwise be persisted silently
        with a stale root-level path. Raises ValueError in both cases.
        """
        objs_list = list(objs)
        seen = set()
        for idx, obj in enumerate(objs_list):
            parent = getattr(obj, 'parent', None)
            if parent is not None and parent.pk is None and id(parent) not in seen:
                # Parent is unsaved and has not yet been encountered. It must appear
                # later in the batch (which is still wrong — children must follow
                # parents) or not at all; either way the trigger would see
                # parent_id=NULL and store this row as a root.
                in_batch_later = any(later is parent for later in objs_list[idx + 1:])
                if in_batch_later:
                    raise ValueError(
                        "bulk_create: child at index {idx} references parent that "
                        "appears later in the same batch; parents must precede "
                        "their children or the child's path will be stored as "
                        "a root.".format(idx=idx)
                    )
                raise ValueError(
                    "bulk_create: child at index {idx} references an unsaved parent "
                    "that is not in this batch; save the parent first or include "
                    "it earlier in the batch — otherwise the child would be "
                    "persisted with a root-level path.".format(idx=idx)
                )
            seen.add(id(obj))
        return super().bulk_create(objs_list, *args, **kwargs)

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
        except Exception:
            field = None
        if isinstance(field, ManyToManyField):
            is_many_to_many = True
        elif isinstance(field, ForeignKey):
            has_direct_fk = True

        has_generic_fk = (
            hasattr(model, 'scope_type') and hasattr(model, 'scope_id')
            and not has_direct_fk and not is_many_to_many
        )

        # Many call sites bind add_related_count() as a class attribute, so it
        # runs at module import. Raising FieldDoesNotExist here would block app
        # startup whenever an unrelated field is renamed; fall back to the
        # Django default column name (`{rel_field}_id`) instead, matching MPTT's
        # add_related_count behavior.
        rel_field_col_default = f'{rel_field}_id'

        qn = connection.ops.quote_name
        parent_table = qn(queryset.model._meta.db_table)
        related_table = qn(model._meta.db_table)

        if cumulative:
            if is_many_to_many:
                field = model._meta.get_field(rel_field)
                m2m_table = qn(field.remote_field.through._meta.db_table)
                # `model` is the declaring side (the side holding the items to count);
                # `queryset.model` is the related (tree) side. m2m_column_name() points
                # at the declaring model; m2m_reverse_name() points at the related model.
                m2m_to_child_col = qn(field.m2m_column_name())
                m2m_to_tree_col = qn(field.m2m_reverse_name())
                sql = f'''(
                    SELECT COUNT(DISTINCT {related_table}."id")
                    FROM {related_table}
                    INNER JOIN {m2m_table}
                      ON {related_table}."id" = {m2m_table}.{m2m_to_child_col}
                    INNER JOIN {parent_table} AS subtree
                      ON {m2m_table}.{m2m_to_tree_col} = subtree."id"
                    WHERE subtree."path" <@ {parent_table}."path"
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
                    SELECT COUNT(DISTINCT {related_table}."id")
                    FROM {related_table}
                    INNER JOIN {parent_table} AS subtree
                      ON {related_table}."scope_id" = subtree."id"
                    WHERE {related_table}."scope_type_id" = (
                        SELECT id FROM django_content_type
                        WHERE app_label = %s AND model = %s
                    )
                      AND subtree."path" <@ {parent_table}."path"
                )'''
                return queryset.annotate(**{
                    count_attr: RawSQL(sql, [ct_app, ct_model], output_field=models.IntegerField())
                })
            # Use field.column (not f'{rel_field}_id') so custom db_column works;
            # fall back to default naming if the field was not resolved.
            rel_field_col = qn(field.column if field is not None else rel_field_col_default)
            sql = f'''(
                    SELECT COUNT(DISTINCT {related_table}."id")
                    FROM {related_table}
                    INNER JOIN {parent_table} AS subtree
                      ON {related_table}.{rel_field_col} = subtree."id"
                    WHERE subtree."path" <@ {parent_table}."path"
                )'''
            return queryset.annotate(**{
                count_attr: RawSQL(sql, [], output_field=models.IntegerField())
            })

        # Non-cumulative: count only rows pointing directly at each node. Mirrors the
        # cumulative branches but joins on equality instead of the `<@` subtree test.
        if is_many_to_many:
            field = model._meta.get_field(rel_field)
            m2m_table = qn(field.remote_field.through._meta.db_table)
            m2m_to_child_col = qn(field.m2m_column_name())
            m2m_to_tree_col = qn(field.m2m_reverse_name())
            sql = f'''(
                SELECT COUNT(DISTINCT {related_table}."id")
                FROM {related_table}
                INNER JOIN {m2m_table}
                  ON {related_table}."id" = {m2m_table}.{m2m_to_child_col}
                WHERE {m2m_table}.{m2m_to_tree_col} = {parent_table}."id"
            )'''
            return queryset.annotate(**{
                count_attr: RawSQL(sql, [], output_field=models.IntegerField())
            })
        if has_generic_fk:
            ct_app = queryset.model._meta.app_label
            ct_model = queryset.model._meta.model_name
            sql = f'''(
                SELECT COUNT(DISTINCT {related_table}."id")
                FROM {related_table}
                WHERE {related_table}."scope_id" = {parent_table}."id"
                  AND {related_table}."scope_type_id" = (
                      SELECT id FROM django_content_type
                      WHERE app_label = %s AND model = %s
                  )
            )'''
            return queryset.annotate(**{
                count_attr: RawSQL(sql, [ct_app, ct_model], output_field=models.IntegerField())
            })
        rel_field_col = qn(field.column if field is not None else rel_field_col_default)
        sql = f'''(
            SELECT COUNT(DISTINCT {related_table}."id")
            FROM {related_table}
            WHERE {related_table}.{rel_field_col} = {parent_table}."id"
        )'''
        return queryset.annotate(**{
            count_attr: RawSQL(sql, [], output_field=models.IntegerField())
        })


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

    Sort-path on rename:
        For subclasses with the optional `sort_path` column (see
        InstallLtreeTriggers' `name_column` arg), renaming a row updates its
        own sort_path AND cascades into descendants' sort_paths via the AFTER
        trigger. This diverges from django-mptt's `order_insertion_by` (which
        leaves both the renamed row and its descendants stale until a manual
        rebuild) because list views are expected to reflect renames promptly.
        `rebuild_sort_paths()` is still available for bulk repair after raw
        SQL writes that bypass the triggers.

    Concurrency:
        Path maintenance takes no table-wide lock (unlike django-mptt, which
        acquired a per-model advisory lock on every write to protect its global
        lft/rght/tree_id numbering). Because a row's path depends only on its
        parent's path, concurrent inserts and moves under *different* parents
        never conflict.

        To keep a node consistent with a concurrently-reparented ancestor, the
        BEFORE trigger reads the parent row `FOR SHARE`. That shared lock conflicts
        with the row-exclusive lock a reparent/rename of the parent takes, so an
        insert/move under P is serialized against a concurrent reparent or rename
        of P (or of an ancestor, whose cascade must update P's row). Sibling
        inserts under a stable parent still proceed concurrently — shared locks
        don't conflict. Crossing reparents (moving A under B while moving B under
        A) can deadlock; PostgreSQL aborts one with a retryable error rather than
        silently persisting a stale path.
    """
    # `default=''` here is a Django-side placeholder that the BEFORE INSERT
    # trigger always overwrites with a valid path before the row reaches
    # storage. Empty ltree (`''`) is itself a valid PostgreSQL ltree value
    # (nlevel = 0) in supported PostgreSQL versions (15+), so even harnesses
    # that bypass the trigger will not fail at INSERT — they will simply
    # store a zero-level path.
    path = LtreeField(editable=False, null=False, blank=True, default='')

    objects = LtreeManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Read from __dict__ rather than via attribute access: a deferred
        # `parent_id`/`name` (e.g. a GraphQL query selecting only a subset of
        # fields) must not be lazily loaded here, since that triggers
        # refresh_from_db() which rebuilds the instance and recurses into __init__.
        self._loaded_parent_id = self.__dict__.get('parent_id')
        self._loaded_name = self.__dict__.get('name')

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_parent_id = instance.__dict__.get('parent_id')
        instance._loaded_name = instance.__dict__.get('name')
        return instance

    def _parent_creates_cycle(self):
        """
        Return True if the current `parent` assignment would make this node its
        own ancestor (the new parent is self or one of its descendants), mirroring
        django-mptt's save-time InvalidMove guard.

        Subclasses whose `parent` is system-managed (e.g. ModuleBay, whose parent
        is derived from its module) may override this to disable the check.
        """
        if self.parent_id is None:
            return False
        # Self-as-parent is always a cycle and must be caught even if self.path
        # is empty or deferred (path would otherwise short-circuit below).
        if self.parent_id == self.pk:
            return True
        if not self.path:
            return False
        # The new parent lies inside this node's current subtree iff its path is a
        # descendant of (or equal to) self.path.
        return type(self)._default_manager.filter(
            pk=self.parent_id, path__descendant_or_equal=self.path
        ).exists()

    def save(self, *args, **kwargs):
        """
        Triggers compute `path` (and `sort_path`, where present) server-side.

        On INSERT the trigger-maintained columns are db_returning, so they are
        populated in-place by the INSERT ... RETURNING clause without an extra
        query. On an UPDATE that changes `parent` or the name column the triggers
        rewrite those columns server-side, so refresh them afterward to keep the
        in-memory instance consistent (e.g. so change logging snapshots the value
        the triggers actually wrote, not a stale one).
        """
        is_insert = self._state.adding
        # When update_fields is supplied and excludes parent, the DB does not see
        # the new parent_id, so the trigger does not fire and _loaded_parent_id
        # must not advance — otherwise a subsequent full save() would mis-detect
        # the (real) parent change as already-applied and leave path stale.
        update_fields = kwargs.get('update_fields')
        parent_written = update_fields is None or 'parent' in update_fields or 'parent_id' in update_fields
        parent_changed = (not is_insert) and parent_written and self.parent_id != self._loaded_parent_id

        # The sort_path trigger also fires on a name change; detect that so the
        # cascaded sort_path can be refreshed below (path-only models have no
        # sort_path and are unaffected by renames).
        has_sort_path = any(f.attname == 'sort_path' for f in self._meta.concrete_fields)
        name_written = update_fields is None or 'name' in update_fields
        name_changed = (
            (not is_insert) and has_sort_path and name_written
            and self.__dict__.get('name') != self._loaded_name
        )

        # Reject cyclic moves before writing, mirroring django-mptt's save-time
        # guard so scripts / bulk callers (which bypass form & serializer clean())
        # cannot silently corrupt the tree.
        if parent_changed and self._parent_creates_cycle():
            raise ValidationError(_("Cannot assign self or a descendant as parent."))

        super().save(*args, **kwargs)

        if (parent_changed or name_changed) and not is_insert:
            # The triggers rewrote path/sort_path on this UPDATE; fetch them back.
            # (INSERT ... RETURNING covers the insert case, so only updates reach here.)
            refresh_fields = [
                fname for fname in ('path', 'sort_path')
                if any(f.attname == fname for f in self._meta.concrete_fields)
            ]
            row = type(self).objects.values_list(*refresh_fields).get(pk=self.pk)
            for fname, value in zip(refresh_fields, row):
                setattr(self, fname, value)

        if is_insert or parent_written:
            self._loaded_parent_id = self.parent_id
        if is_insert or name_written:
            self._loaded_name = self.__dict__.get('name')

    # -- MPTT-compatible API ------------------------------------------------

    @property
    def level(self):
        """Zero-based depth (root = 0). Mirrors django-mptt's `level`."""
        if not self.path:
            return 0
        return str(self.path).count('.')

    def get_level(self):
        return self.level

    def _root_pk(self):
        """
        Integer PK of the root node, parsed from the first (zero-padded) path label.
        Returns None for a node with no path.
        """
        if not self.path:
            return None
        return int(str(self.path).split('.', 1)[0].lstrip('0') or '0')

    @property
    def tree_id(self):
        """Integer PK of the root, mirroring django-mptt's `tree_id`."""
        return self._root_pk()

    def is_root_node(self):
        return self.parent_id is None

    def is_leaf_node(self):
        return not type(self).objects.filter(parent_id=self.pk).exists()

    def is_child_node(self):
        return self.parent_id is not None

    def get_root(self):
        if self.is_root_node():
            return self
        return type(self)._default_manager.get(pk=self._root_pk())

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
        lookup = 'descendant_or_equal' if include_self else 'descendant'
        return type(self)._default_manager.filter(**{f'path__{lookup}': self.path}).order_by('path')

    def get_descendant_count(self):
        if not self.path:
            return 0
        return type(self)._default_manager.filter(path__descendant=self.path).count()

    def get_children(self):
        return type(self)._default_manager.filter(parent_id=self.pk)

    def get_family(self):
        """Ancestors + self + descendants, in path order."""
        if not self.path:
            return type(self)._default_manager.none()
        return type(self)._default_manager.filter(
            Q(path__ancestor=self.path) | Q(path__descendant_or_equal=self.path)
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

        Inserts, reparents, AND renames are all maintained automatically by the
        BEFORE/AFTER triggers (the BEFORE trigger fires on INSERT and on updates to
        parent_id or the name column). Use this only to repair `sort_path` after a
        raw SQL write (e.g. a bulk COPY or a direct UPDATE) that bypassed those
        triggers.

        Raises if the table does not have a `sort_path` column.
        """
        from django.db import connection

        if not any(f.name == 'sort_path' for f in cls._meta.get_fields()):
            raise NotImplementedError(
                f"{cls.__name__} does not have a sort_path column"
            )
        qn = connection.ops.quote_name
        table = qn(cls._meta.db_table)
        name_col = qn(name_column)
        sql = f'''
            WITH RECURSIVE t(id, parent_id, sort_path) AS (
                SELECT id, parent_id, {name_col}::text
                FROM {table} WHERE parent_id IS NULL
                UNION ALL
                SELECT r.id, r.parent_id, t.sort_path || chr(9) || r.{name_col}
                FROM {table} r INNER JOIN t ON r.parent_id = t.id
            )
            UPDATE {table} SET sort_path = t.sort_path FROM t WHERE {table}.id = t.id;
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
        -- FOR SHARE locks the parent row so a concurrent reparent/rename of it
        -- (or of an ancestor, whose cascade updates this parent's row) cannot
        -- proceed until this insert/move commits, preventing a stale path.
        EXECUTE format('SELECT path FROM %%I WHERE id = $1 FOR SHARE', TG_TABLE_NAME)
            INTO parent_path USING NEW.parent_id;
        -- Cycle guard. The Python LtreeModel.save() also rejects cyclic moves,
        -- but a QuerySet.update() / bulk_update() bypasses save() entirely, so
        -- catch the case here as a last line of defense. lpad(NEW.id,..) @>
        -- parent_path is TRUE iff parent_path starts with this row's own
        -- label (i.e. the proposed parent is self or one of self's descendants).
        IF lpad(NEW.id::text, 19, '0')::ltree @> parent_path THEN
            RAISE EXCEPTION 'cycle detected: %% cannot be assigned a parent that is itself or one of its descendants', TG_TABLE_NAME
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
BEGIN
    IF NEW.parent_id IS NOT NULL THEN
        -- FOR SHARE locks the parent row so a concurrent reparent/rename of it
        -- (or of an ancestor, whose cascade updates this parent's row) cannot
        -- proceed until this insert/move commits, preventing a stale path/sort_path.
        EXECUTE format('SELECT path, sort_path FROM %%I WHERE id = $1 FOR SHARE', TG_TABLE_NAME)
            INTO parent_path, parent_sort_path USING NEW.parent_id;
        -- Cycle guard. See _COMPUTE_PATH_ONLY_FN for the rationale; this catches
        -- raw UPDATE / bulk_update paths that bypass LtreeModel.save().
        IF lpad(NEW.id::text, 19, '0')::ltree @> parent_path THEN
            RAISE EXCEPTION 'cycle detected: %% cannot be assigned a parent that is itself or one of its descendants', TG_TABLE_NAME
                USING ERRCODE = 'check_violation';
        END IF;
        NEW.path := parent_path || lpad(NEW.id::text, 19, '0')::ltree;
        NEW.sort_path := parent_sort_path || chr(9) || NEW.{name_col};
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
