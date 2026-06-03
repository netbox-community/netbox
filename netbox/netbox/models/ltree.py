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
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError, OperationalError, connection, migrations, models
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
        Same as the standard `bulk_create` but rejects any row whose parent is an
        unsaved instance. Django's bulk_create builds the multi-row INSERT VALUES
        up front from each instance's `parent_id`; an unsaved parent's pk is not
        assigned until the INSERT's RETURNING clause executes, so a child
        referencing an unsaved parent (even one earlier in the same batch) goes
        in with parent_id=NULL and the BEFORE trigger stores it as a root. Save
        the parents first, then bulk_create their children.
        """
        objs_list = list(objs)
        for idx, obj in enumerate(objs_list):
            parent = getattr(obj, 'parent', None)
            if parent is not None and parent.pk is None:
                raise ValueError(
                    "bulk_create: child at index {idx} references an unsaved parent. "
                    "Django cannot propagate the parent's RETURNING-assigned pk into "
                    "the child's parent_id before the INSERT executes, so the child "
                    "would be persisted with parent_id=NULL and stored as a root. "
                    "Save the parent first, then bulk_create the children.".format(idx=idx)
                )
        return super().bulk_create(objs_list, *args, **kwargs)

    def add_related_count(self, queryset, model, rel_field, count_attr, cumulative=False):
        """
        Annotate `queryset` with the count of `model` instances related via
        `rel_field`, mirroring django-mptt's `TreeManager.add_related_count`.

        When `cumulative=True`, counts include rows pointing to any descendant
        (using the ltree `<@` operator against the parent's `path`). Handles
        ForeignKey, ManyToManyField, and the NetBox GenericForeignKey "scope"
        pattern (scope_type / scope_id).

        The six historical variants (3 relation kinds × cumulative/not) are
        assembled from two fragments: how a related row links to a tree node
        (`link_expr` + any join/scope filter), and which node is counted — the
        parent row itself (non-cumulative) or any node in its subtree via `<@`
        (cumulative).
        """
        try:
            field = model._meta.get_field(rel_field)
        except Exception:
            field = None
        is_many_to_many = isinstance(field, ManyToManyField)
        has_direct_fk = isinstance(field, ForeignKey)
        has_generic_fk = (
            hasattr(model, 'scope_type') and hasattr(model, 'scope_id')
            and not has_direct_fk and not is_many_to_many
        )

        qn = connection.ops.quote_name
        parent_table = qn(queryset.model._meta.db_table)
        related_table = qn(model._meta.db_table)

        # `from_join` is the FROM (+ m2m join); `link_expr` is the column that points
        # at a tree node's id; `scope_filter` constrains the generic-FK content type.
        params = []
        from_join = f'FROM {related_table}'
        scope_filter = ''
        if is_many_to_many:
            # m2m_column_name() points at the declaring model (`model`);
            # m2m_reverse_name() points at the related (tree) model.
            m2m_table = qn(field.remote_field.through._meta.db_table)
            from_join += (
                f' INNER JOIN {m2m_table}'
                f' ON {related_table}."id" = {m2m_table}.{qn(field.m2m_column_name())}'
            )
            link_expr = f'{m2m_table}.{qn(field.m2m_reverse_name())}'
        elif has_generic_fk:
            link_expr = f'{related_table}."scope_id"'
            # Resolve scope_type_id via subquery so the annotation can be built at
            # import time (e.g. in a view class body) before contenttypes migrate.
            scope_filter = (
                f' AND {related_table}."scope_type_id" = ('
                'SELECT id FROM django_content_type WHERE app_label = %s AND model = %s)'
            )
            params = [queryset.model._meta.app_label, queryset.model._meta.model_name]
        else:
            # field.column honors a custom db_column; fall back to Django's default
            # `{rel_field}_id` if the field was not resolved (a renamed unrelated
            # field must not break import-time annotation construction).
            rel_field_col = qn(field.column if field is not None else f'{rel_field}_id')
            link_expr = f'{related_table}.{rel_field_col}'

        if cumulative:
            node_join = f' INNER JOIN {parent_table} AS subtree ON {link_expr} = subtree."id"'
            where = f'WHERE subtree."path" <@ {parent_table}."path"{scope_filter}'
        else:
            node_join = ''
            where = f'WHERE {link_expr} = {parent_table}."id"{scope_filter}'

        sql = f'(SELECT COUNT(DISTINCT {related_table}."id") {from_join}{node_join} {where})'
        return queryset.annotate(**{
            count_attr: RawSQL(sql, params, output_field=models.IntegerField())
        })


class LtreeManager(models.Manager.from_queryset(LtreeQuerySet)):
    """Drop-in replacement for django-mptt's TreeManager."""


#
# Abstract model
#

class LtreeModelBase(models.base.ModelBase):
    """
    Metaclass that keeps a model's `sort_path` collation in sync with its `name`.

    `sort_path` holds a chr(9)-joined chain of ancestor names, so to flatten siblings
    in the same order the database sorts `name`, the two columns must share a collation.
    Deriving it here means a subclass that gives `name` a custom db_collation (e.g.
    `natural_sort`) automatically gets a matching `sort_path` — no need to redeclare the
    field just to repeat the collation. An explicit db_collation on `sort_path` is left
    untouched.
    """
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if cls._meta.abstract:
            return cls
        try:
            name_field = cls._meta.get_field('name')
            sort_path_field = cls._meta.get_field('sort_path')
        except FieldDoesNotExist:
            return cls
        name_collation = getattr(name_field, 'db_collation', None)
        if name_collation and not getattr(sort_path_field, 'db_collation', None):
            sort_path_field.db_collation = name_collation
        return cls


class LtreeModel(models.Model, metaclass=LtreeModelBase):
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
        acquired a per-model advisory lock on *every* write to protect its global
        lft/rght/tree_id numbering). Instead, the BEFORE trigger serializes per
        tree: it takes a transaction-level advisory lock keyed on the root of the
        tree being written (and, for a cross-tree move, on both the source and
        destination roots, acquired in ascending key order to avoid deadlocks).

        Every insert, move, and reparent of a node in a tree takes the same key,
        so an insert deep in a subtree and a concurrent reparent of one of its
        ancestors are serialized — the loser blocks until the winner commits, and
        the winner's AFTER cascade can never miss a row inserted concurrently
        (which a row-level `FOR SHARE` on the parent could not prevent: a set-based
        cascade's snapshot would skip a row inserted after it began). Writes to
        *different* trees use different keys and proceed fully in parallel — e.g.
        inventory ingestion across different devices, each its own tree.

        Two residual, retryable cases remain (PostgreSQL aborts one transaction
        with a deadlock error rather than persisting a stale path): crossing
        reparents (moving A under B while moving B under A), and two concurrent
        *moves* in an ancestor/descendant relationship (a move locks the moved
        row before its BEFORE trigger can take the advisory lock). Plain inserts
        — the high-volume path — never hit this.
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

    @classmethod
    def _has_sort_path(cls):
        """
        Whether this model carries the optional trigger-maintained `sort_path`
        column (the MPTT `order_insertion_by=('name',)` equivalent). Single source
        of truth for clean(), save(), and _tree_order_field().
        """
        return any(f.attname == 'sort_path' for f in cls._meta.concrete_fields)

    def clean(self):
        """
        Reject assigning self or a descendant as parent, surfacing it as a field
        error for forms/serializers. This mirrors the save()-time guard; the two
        share _parent_creates_cycle() so the rule lives in exactly one place.

        Subclasses whose `parent` is system-managed (e.g. ModuleBay) disable the
        check by overriding _parent_creates_cycle() to return False.

        For sort_path-backed models, also reject a tab in the name column: sort_path
        joins ancestor names with chr(9) (TAB), so a literal tab in a name would
        corrupt sibling ordering for the node and its descendants.
        """
        super().clean()

        if self.pk and self._parent_creates_cycle():
            raise ValidationError({
                "parent": _("Cannot assign self or a descendant as parent.")
            })

        if self._has_sort_path() and '\t' in (getattr(self, 'name', None) or ''):
            raise ValidationError({
                "name": _("Name cannot contain tab characters.")
            })

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
        has_sort_path = self._has_sort_path()
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

        try:
            super().save(*args, **kwargs)
        except IntegrityError as exc:
            # A concurrent reparent that races the Python-level _parent_creates_cycle
            # check is caught by the BEFORE trigger, which RAISEs 'cycle detected ...'
            # with ERRCODE = check_violation (SQLSTATE 23514). Gate on the SQLSTATE
            # (the primary, stable signal) AND the message marker, so an unrelated
            # CHECK constraint on a subclass (also 23514) is not misreported as a
            # cycle. Surface it as a ValidationError so the API/UI returns 400 instead
            # of the IntegrityError → 500 the trigger would otherwise produce.
            if (
                getattr(exc.__cause__, 'sqlstate', None) == '23514'
                and 'cycle detected' in str(exc)
            ):
                raise ValidationError(
                    _("Cannot assign self or a descendant as parent.")
                ) from None
            # The BEFORE trigger likewise rejects a tab in the name (it would corrupt
            # sort_path); translate it for direct save() calls that skip clean().
            if (
                getattr(exc.__cause__, 'sqlstate', None) == '23514'
                and 'tab character' in str(exc)
            ):
                raise ValidationError({
                    "name": _("Name cannot contain tab characters.")
                }) from None
            raise
        except OperationalError as exc:
            # The per-tree advisory locks can deadlock on crossing reparents or two
            # concurrent ancestor/descendant moves; PostgreSQL aborts one with
            # SQLSTATE 40P01. Surface a clear, retryable message instead of the
            # opaque 500 the bare OperationalError would produce.
            if getattr(exc.__cause__, 'sqlstate', None) == '40P01':
                raise ValidationError(
                    _("The hierarchy was modified concurrently; please retry.")
                ) from None
            raise

        if (parent_changed or name_changed) and not is_insert:
            # The triggers rewrote path/sort_path on this UPDATE; fetch them back so
            # the in-memory instance matches storage (e.g. so change logging snapshots
            # the value the triggers wrote, not a stale one). This costs one extra
            # SELECT per reparent/rename; INSERT ... RETURNING covers the insert case,
            # so only updates reach here.
            refresh_fields = ['path'] + (['sort_path'] if has_sort_path else [])
            self.refresh_from_db(fields=refresh_fields)

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
        if self.pk is None:
            # Unsaved instance has no children. Without this guard,
            # filter(parent_id=None) would match every existing root.
            return True
        return not type(self).objects.filter(parent_id=self.pk).exists()

    def is_child_node(self):
        return self.parent_id is not None

    def get_root(self):
        if self.is_root_node():
            return self
        if not self.path:
            # Unsaved (no path computed yet). Walk up the in-memory parent
            # chain if available; otherwise we have no way to resolve the root.
            parent = getattr(self, 'parent', None)
            return parent.get_root() if parent is not None else None
        return type(self)._default_manager.get(pk=self._root_pk())

    def get_parent(self):
        return self.parent

    @classmethod
    def _tree_order_field(cls):
        """
        Field name to order hierarchical queries by. Models that carry a
        `sort_path` column (the MPTT `order_insertion_by=('name',)` equivalent)
        order siblings by name to match the prior MPTT behavior; models
        without it fall back to `path` (PK-padded, insertion order).
        """
        return 'sort_path' if cls._has_sort_path() else 'path'

    def get_ancestors(self, ascending=False, include_self=False):
        if not self.path:
            return type(self)._default_manager.none()
        qs = type(self)._default_manager.filter(path__ancestor=self.path)
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        order_field = self._tree_order_field()
        return qs.order_by(f'-{order_field}' if ascending else order_field)

    def get_descendants(self, include_self=False):
        if not self.path:
            return type(self)._default_manager.none()
        lookup = 'descendant_or_equal' if include_self else 'descendant'
        return type(self)._default_manager.filter(
            **{f'path__{lookup}': self.path}
        ).order_by(self._tree_order_field())

    def get_descendant_count(self):
        if not self.path:
            return 0
        return type(self)._default_manager.filter(path__descendant=self.path).count()

    def get_children(self):
        return type(self)._default_manager.filter(parent_id=self.pk).order_by(self._tree_order_field())

    def get_family(self):
        """Ancestors + self + descendants, in tree-order."""
        if not self.path:
            return type(self)._default_manager.none()
        # No .distinct() needed: this is a single-table OR with no joins, so a row
        # (self, which matches both branches) is still returned only once.
        return type(self)._default_manager.filter(
            Q(path__ancestor=self.path) | Q(path__descendant_or_equal=self.path)
        ).order_by(self._tree_order_field())

    def get_siblings(self, include_self=False):
        qs = type(self)._default_manager.filter(parent_id=self.parent_id)
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs.order_by(self._tree_order_field())

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

        if not cls._has_sort_path():
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
# Per-tree advisory locking (see _lock_tree_roots_sql / LtreeModel "Concurrency"):
# every insert/move/reparent of a node takes a transaction-level advisory lock
# keyed on the root(s) of the tree(s) it touches, BEFORE reading the parent path.
# A concurrent reparent of an ancestor takes the same key, so the two serialize
# and the AFTER cascade can never miss a row inserted concurrently; writes in
# different trees use different keys and run in parallel.
_LOCK_TREE_ROOTS_SQL = '''
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
