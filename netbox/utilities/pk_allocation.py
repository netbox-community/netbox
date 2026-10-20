from django.db import models
from django.db.models.fields import AutoFieldMixin

from netbox.utils import allocate_pks

__all__ = (
    'prepare_for_bulk_create_with_pk_allocation',
    'save_table_with_pk_allocation',
)

_prepare_for_bulk_create = models.QuerySet._prepare_for_bulk_create
_save_table = models.Model._save_table


def save_table_with_pk_allocation(
    instance, raw=False, cls=None, force_insert=False, force_update=False, using=None, update_fields=None
):
    """
    Imitate the behavior of the stock Model._save_table() method, but first consult any registered primary key
    allocators for a new object without a primary key. If an allocator supplies one, insert the object directly:
    Django would otherwise attempt an UPDATE using the allocated primary key first, overwriting any existing row which
    shares it. Objects saved with a primary key already set, and forced updates (which require one), are unaffected.

    Allocators receive the model which owns the primary key column (the concrete parent, for a proxy or multi-table
    inheritance child), and the alias of the database being written to.
    """
    pk = cls._meta.pk
    if (
        isinstance(pk, AutoFieldMixin)
        and not (force_update or update_fields)
        and not instance._is_pk_set(cls._meta)
        and (pks := allocate_pks(pk.model, using=using))
    ):
        setattr(instance, pk.attname, pks[0])
        force_insert = True
    return _save_table(instance, raw, cls, force_insert, force_update, using, update_fields)


def prepare_for_bulk_create_with_pk_allocation(queryset, objs):
    """
    Imitate the behavior of the stock QuerySet._prepare_for_bulk_create() method, but first consult any registered
    primary key allocators for the objects without a primary key, requesting all of their primary keys in a single
    call. Objects which receive one are inserted along with any whose primary key was already set.
    """
    pk = queryset.model._meta.pk
    if isinstance(pk, AutoFieldMixin):
        new_objs = [obj for obj in objs if not obj._is_pk_set()]
        # QuerySet.db resolves to the database being written to, since bulk_create() has already set _for_write
        if new_objs and (pks := allocate_pks(pk.model, len(new_objs), using=queryset.db)):
            for obj, pk_value in zip(new_objs, pks):
                setattr(obj, pk.attname, pk_value)
    return _prepare_for_bulk_create(queryset, objs)
