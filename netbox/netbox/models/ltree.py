"""
Ltree-based hierarchical model support - a replacement for django-mptt backed by
a PostgreSQL ltree column.

LtreeModel covers the subset of django-mptt's MPTTModel API that NetBox actually
uses. It is deliberately NOT a full reimplementation of MPTT's surface — methods
NetBox does not rely on (e.g. get_leafnodes(), get_next_sibling(),
get_previous_sibling()) are intentionally omitted.

Paths are maintained entirely by PostgreSQL triggers installed via the
InstallLtreeTriggers migration operation. The Python layer never computes or
mutates paths directly; it only reads `path` back from the database after
inserts and parent_id changes via refresh_from_db(fields=['path']).
"""
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError, OperationalError, connection, models
from django.db.models import ForeignKey, ManyToManyField
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from utilities.querysets import RestrictedQuerySet

from . import lookups

__all__ = (
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


LtreeField.register_lookup(lookups.Ancestor)
LtreeField.register_lookup(lookups.AncestorOrEqual)
LtreeField.register_lookup(lookups.Descendant)
LtreeField.register_lookup(lookups.DescendantOrEqual)


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
        The BEFORE INSERT trigger resolves a row's parent by SELECTing `path`
        from the same table by parent_id. LtreeQuerySet.bulk_create() rejects any
        row whose parent is an *unsaved* instance, so in normal use — parents
        saved before their children are bulk-created — batch order does not matter
        (each parent row already exists for the lookup). The lone exception is
        manually pre-assigned PKs: if a child references a same-batch parent by a
        hand-set pk, that parent must appear earlier in the batch (the BEFORE
        trigger fires per row in list order), or the child gets a root-level path.

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
        try:
            cls._meta.get_field('sort_path')
            return True
        except FieldDoesNotExist:
            return False

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

        # Reject cyclic moves before writing, mirroring django-mptt's save-time
        # guard so scripts / bulk callers (which bypass form & serializer clean())
        # cannot silently corrupt the tree.
        if parent_changed and self._parent_creates_cycle():
            raise ValidationError(_("Cannot assign self or a descendant as parent."))

        # The sort_path trigger also fires on a name change; detect that so the
        # cascaded sort_path can be refreshed below (path-only models have no
        # sort_path and are unaffected by renames).
        has_sort_path = self._has_sort_path()
        name_written = update_fields is None or 'name' in update_fields
        name_changed = (
            (not is_insert) and has_sort_path and name_written
            and self.__dict__.get('name') != self._loaded_name
        )

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
        lookup = 'ancestor_or_equal' if include_self else 'ancestor'
        qs = type(self)._default_manager.filter(**{f'path__{lookup}': self.path})
        order_field = self._tree_order_field()
        return qs.order_by(f'-{order_field}' if ascending else order_field)

    def get_descendants(self, include_self=False):
        if not self.path:
            return type(self)._default_manager.none()
        lookup = 'descendant_or_equal' if include_self else 'descendant'
        return type(self)._default_manager.filter(
            **{f'path__{lookup}': self.path}
        ).order_by(self._tree_order_field())

    def get_children(self):
        return type(self)._default_manager.filter(parent_id=self.pk).order_by(self._tree_order_field())

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
