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
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models
from django.db.models import Count, ForeignKey, ManyToManyField, Lookup, OuterRef, Q, Subquery
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
                m2m_parent_col = field.m2m_column_name()
                m2m_related_col = field.m2m_reverse_name()
                sql = f'''(
                    SELECT COUNT(DISTINCT "{related_table}"."id")
                    FROM "{related_table}"
                    INNER JOIN "{m2m_table}"
                      ON "{related_table}"."id" = "{m2m_table}"."{m2m_related_col}"
                    INNER JOIN "{parent_table}" AS subtree
                      ON "{m2m_table}"."{m2m_parent_col}" = subtree."id"
                    WHERE subtree."path" <@ "{parent_table}"."path"
                )'''
                return queryset.annotate(**{
                    count_attr: RawSQL(sql, [], output_field=models.IntegerField())
                })
            elif has_generic_fk:
                content_type = ContentType.objects.get_for_model(queryset.model)
                sql = f'''(
                    SELECT COUNT(DISTINCT "{related_table}"."id")
                    FROM "{related_table}"
                    INNER JOIN "{parent_table}" AS subtree
                      ON "{related_table}"."scope_id" = subtree."id"
                    WHERE "{related_table}"."scope_type_id" = %s
                      AND subtree."path" <@ "{parent_table}"."path"
                )'''
                return queryset.annotate(**{
                    count_attr: RawSQL(sql, [content_type.pk], output_field=models.IntegerField())
                })
            else:
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
            content_type = ContentType.objects.get_for_model(queryset.model)
            subquery = model.objects.filter(
                scope_type=content_type, scope_id=OuterRef('pk')
            ).values('scope_id').annotate(c=Count('id')).values('c')
            return queryset.annotate(**{
                count_attr: Subquery(subquery, output_field=models.IntegerField())
            })
        return queryset.annotate(**{count_attr: Count(rel_field, distinct=True)})


class LtreeManager(models.Manager.from_queryset(LtreeQuerySet)):
    """Drop-in replacement for django-mptt's TreeManager."""

    def get_queryset(self):
        return super().get_queryset().order_by('path')


#
# Abstract model
#

class LtreeModel(models.Model):
    """
    Abstract base for hierarchical models backed by PostgreSQL ltree.

    Subclasses must declare a `parent = models.ForeignKey('self', ...)`. The
    `path` column is maintained by per-table triggers installed via
    InstallLtreeTriggers; do not write to it from Python.
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
        Triggers compute `path` server-side. After insert or after a parent
        change, refresh just the path column so the in-memory instance stays
        consistent with the database.
        """
        is_insert = self._state.adding
        parent_changed = (not is_insert) and self.parent_id != self._loaded_parent_id
        super().save(*args, **kwargs)
        if is_insert or parent_changed:
            self.path = type(self).objects.values_list('path', flat=True).get(pk=self.pk)
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
        root_label = str(self.path).split('.', 1)[0]
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
        root_pk = int(str(self.path).split('.', 1)[0])
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


#
# Migration operation
#

_COMPUTE_PATH_FN = '''
CREATE OR REPLACE FUNCTION "{table}_ltree_compute_path_fn"() RETURNS TRIGGER AS $$
DECLARE parent_path ltree;
BEGIN
    IF NEW.parent_id IS NOT NULL THEN
        EXECUTE format('SELECT path FROM %%I WHERE id = $1', TG_TABLE_NAME)
            INTO parent_path USING NEW.parent_id;
        NEW.path := parent_path || NEW.id::text::ltree;
    ELSE
        NEW.path := NEW.id::text::ltree;
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
'''

_CASCADE_PATH_FN = '''
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

_BEFORE_TRIGGER = '''
CREATE TRIGGER "{table}_ltree_compute_path"
    BEFORE INSERT OR UPDATE OF parent_id ON "{table}"
    FOR EACH ROW EXECUTE FUNCTION "{table}_ltree_compute_path_fn"();
'''

_AFTER_TRIGGER = '''
CREATE TRIGGER "{table}_ltree_cascade_path"
    AFTER UPDATE OF parent_id, path ON "{table}"
    FOR EACH ROW WHEN (OLD.path IS DISTINCT FROM NEW.path)
    EXECUTE FUNCTION "{table}_ltree_cascade_path_fn"();
'''


class InstallLtreeTriggers(migrations.operations.base.Operation):
    """
    Install per-table ltree path-maintenance triggers.

    Two row-level triggers are installed on each target table:

        BEFORE INSERT OR UPDATE OF parent_id -> compute NEW.path
        AFTER UPDATE OF path WHEN distinct   -> cascade path change to descendants

    The trigger function bodies use TG_TABLE_NAME so the SQL is table-agnostic,
    but each table gets its own pair of CREATE FUNCTION statements to keep
    pg_proc entries identifiable and to avoid surprising cross-table coupling.
    """
    reversible = True

    def __init__(self, table_name):
        self.table_name = table_name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(_COMPUTE_PATH_FN.format(table=self.table_name))
        schema_editor.execute(_CASCADE_PATH_FN.format(table=self.table_name))
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
