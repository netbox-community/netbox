from django.db import models, router
from django.db.models.fields import AutoFieldMixin

from netbox.registry import registry

__all__ = (
    'allocate_pks',
    'bulk_create_with_pk_allocation',
    'prepare_for_bulk_create_with_pk_allocation',
    'register_pk_allocator',
    'save_table_with_pk_allocation',
)

# The stock methods replaced by the functions below. Callers may pass arguments to these positionally, so each
# function's signature must match that of the method it replaces; a test verifies this.
_bulk_create = models.QuerySet.bulk_create
_prepare_for_bulk_create = models.QuerySet._prepare_for_bulk_create
_save_table = models.Model._save_table


def register_pk_allocator(func):
    """
    Decorator for registering a primary key allocator: a callable which may supply primary keys for new objects.

    The callable must accept a model class, a count, and the alias of the database to which the new objects will be
    written (`using`), and return either a list of exactly `count` primary keys for that model, or None to defer to the
    next allocator (and ultimately to the database). Allocators are consulted in the order in which they were
    registered. Registering an allocator which is already registered has no effect.

        @register_pk_allocator
        def my_allocator(model, count, using):
            ...
    """
    if func not in registry['pk_allocators']:
        registry['pk_allocators'].append(func)

    return func


def allocate_pks(model, count=1, using=None):
    """
    Return a list of `count` primary keys for new instances of `model` from the first registered allocator which
    supplies them, or None if the database should assign them. `using` is the alias of the database to which the new
    instances will be written; if omitted, the database router's choice for writing `model` is assumed. Code which
    inserts rows outside the ORM (e.g. using raw SQL or COPY) can call this to obtain primary keys in the same manner
    as Model.save() and QuerySet.bulk_create().
    """
    if using is None:
        using = router.db_for_write(model)
    # Allocators receive the model which owns the primary key column (the concrete parent, for a proxy or multi-table
    # inheritance child), and only if it's an auto field
    pk = model._meta.pk
    while pk.remote_field and pk.remote_field.parent_link:
        pk = pk.target_field
    if not isinstance(pk, AutoFieldMixin):
        return None
    model = pk.model
    for allocator in registry['pk_allocators']:
        if (pks := allocator(model, count, using)) is not None:
            pks = list(pks)
            if len(pks) != count:
                name = getattr(allocator, '__qualname__', allocator)
                raise ValueError(
                    f'Primary key allocator {name} returned {len(pks)} primary keys for {model._meta.label} '
                    f'(expected {count}).'
                )
            return pks
    return None


def _can_allocate_pks(model):
    """
    Return True if primary keys for new instances of the model may be obtained from the registered allocators.
    """
    return bool(registry['pk_allocators']) and isinstance(model._meta.pk, AutoFieldMixin)


def save_table_with_pk_allocation(
    instance, raw=False, cls=None, force_insert=False, force_update=False, using=None, update_fields=None
):
    """
    Imitate the behavior of the stock Model._save_table() method, but first consult any registered primary key
    allocators for a new object without a primary key. If an allocator supplies one, insert the object directly:
    Django would otherwise attempt an UPDATE using the allocated primary key first, overwriting any existing row which
    shares it. Objects saved with a primary key already set, and forced updates (which require one), are unaffected.

    If the INSERT fails, or that of a multi-table inheritance child following it, the allocated primary key is withdrawn
    from the object, so that saving it again consults the allocators again, rather than attempting an UPDATE of
    whichever row has the allocated primary key.

    Allocators receive the model which owns the primary key column (the concrete parent, for a proxy or multi-table
    inheritance child), and the alias of the database being written to.
    """
    pk = cls._meta.pk
    concrete_model = instance._meta.concrete_model
    # The values to restore if the save fails, carried over from the insertion of any multi-table inheritance parents
    unallocated = vars(instance).pop('_unallocated_pks', {})
    try:
        if (
            _can_allocate_pks(cls)
            and not (force_update or update_fields)
            and not instance._is_pk_set(cls._meta)
            and (pks := allocate_pks(cls, using=using))
        ):
            # Parent links are set from the allocated primary key once the parent has been inserted
            parent_links = [
                field.attname
                for model in (concrete_model, *concrete_model._meta.get_parent_list())
                for field in model._meta.parents.values() if field
            ]
            for attname in (pk.attname, *parent_links):
                unallocated.setdefault(attname, getattr(instance, attname))
            setattr(instance, pk.attname, pks[0])
            force_insert = True
        updated = _save_table(
            instance, raw=raw, cls=cls, force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )
    except BaseException:
        for attname, value in unallocated.items():
            setattr(instance, attname, value)
        raise
    if unallocated and cls is not concrete_model:
        # This is a multi-table inheritance parent, whose child has yet to be inserted
        instance._unallocated_pks = unallocated
    return updated


def prepare_for_bulk_create_with_pk_allocation(queryset, objs):
    """
    Imitate the behavior of the stock QuerySet._prepare_for_bulk_create() method, but then consult any registered
    primary key allocators for the objects without a primary key, requesting all of their primary keys in a single
    call. Objects which receive one are inserted along with any whose primary key was already set. Allocators are
    consulted only once the objects have been validated, so that a failed validation doesn't consume primary keys.
    The prior state of each object which receives one is recorded on the queryset, for bulk_create_with_pk_allocation()
    to restore.
    """
    objs_with_pk, objs_without_pk = _prepare_for_bulk_create(queryset, objs)
    pk = queryset.model._meta.pk
    # QuerySet.db resolves to the database being written to, since bulk_create() has already set _for_write
    if (
        objs_without_pk
        and _can_allocate_pks(queryset.model)
        and (pks := allocate_pks(queryset.model, len(objs_without_pk), using=queryset.db))
    ):
        queryset._unallocated_pks = [
            (obj, getattr(obj, pk.attname), obj._state.adding, obj._state.db) for obj in objs_without_pk
        ]
        for obj, pk_value in zip(objs_without_pk, pks):
            setattr(obj, pk.attname, pk_value)
        # Every object now has a primary key, so insert them all together, in their original order
        return list(objs), []
    return objs_with_pk, objs_without_pk


def bulk_create_with_pk_allocation(
    queryset, objs, batch_size=None, ignore_conflicts=False, update_conflicts=False, update_fields=None,
    unique_fields=None
):
    """
    Wrap the stock QuerySet.bulk_create() method to withdraw allocated primary keys from objects which might not have
    been inserted, leaving them as bulk_create() would without an allocator:

      * If the operation fails, so that saving the objects again consults the allocators again, rather than attempting
        an UPDATE of whichever rows have the allocated primary keys.
      * If conflicting rows are ignored, since there's no telling which objects were inserted. (bulk_create() never
        sets primary keys in this case.)
    """
    pk = queryset.model._meta.pk

    def withdraw_allocated_pks():
        # Restore any objects to which prepare_for_bulk_create_with_pk_allocation() allocated primary keys
        for obj, pk_value, adding, db in vars(queryset).pop('_unallocated_pks', ()):
            setattr(obj, pk.attname, pk_value)
            obj._state.adding = adding
            obj._state.db = db

    try:
        objs = _bulk_create(
            queryset, objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts, update_fields=update_fields, unique_fields=unique_fields
        )
    except BaseException:
        withdraw_allocated_pks()
        raise
    if ignore_conflicts:
        withdraw_allocated_pks()
    else:
        vars(queryset).pop('_unallocated_pks', None)
    return objs


# Like the stock method, prevent templates from calling this
bulk_create_with_pk_allocation.alters_data = True
