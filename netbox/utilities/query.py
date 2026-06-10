from django.db.models import Count, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce

__all__ = (
    'count_related',
    'dict_to_filter_params',
    'reapply_model_ordering',
)


def count_related(model, field):
    """
    Return a Subquery suitable for annotating a child object count.
    """
    subquery = Subquery(
        model.objects.filter(
            **{field: OuterRef('pk')}
        ).order_by().values(
            field
        ).annotate(
            c=Count('*')
        ).values('c')
    )

    return Coalesce(subquery, 0)


def dict_to_filter_params(d, prefix=''):
    """
    Translate a dictionary of attributes to a nested set of parameters suitable for QuerySet filtering. For example:

        {
            "name": "Foo",
            "rack": {
                "facility_id": "R101"
            }
        }

    Becomes:

        {
            "name": "Foo",
            "rack__facility_id": "R101"
        }

    And can be employed as filter parameters:

        Device.objects.filter(**dict_to_filter(attrs_dict))
    """
    params = {}
    for key, val in d.items():
        k = prefix + key
        if isinstance(val, dict):
            params.update(dict_to_filter_params(val, k + '__'))
        else:
            params[k] = val
    return params


# TODO: Remove in NetBox v5.0. MPTT support is retained only for plugins that have
# not yet migrated their tree models to netbox.models.ltree.LtreeModel; NetBox core
# no longer uses django-mptt. When MPTT support is dropped, delete this helper and
# its call in reapply_model_ordering().
def _is_mptt_model(model) -> bool:
    """
    Whether `model` is backed by django-mptt (deprecated). MPTT applies its own
    tree ordering via the TreeManager, so such querysets must NOT have plain
    model-level ordering reapplied after .annotate().
    """
    from mptt.managers import TreeManager

    return any(isinstance(manager, TreeManager) for manager in model._meta.local_managers)


def reapply_model_ordering(queryset: QuerySet) -> QuerySet:
    """
    Reapply model-level ordering in case it has been lost through .annotate().
    https://code.djangoproject.com/ticket/32811
    """
    # Models ordered by a trigger-maintained ltree column (`sort_path`/`path`) are
    # exempt. Key the check on the ordering itself, NOT on LtreeManager presence:
    # InventoryItem/InventoryItemTemplate use an LtreeManager only for path
    # maintenance but order by a regular column (name), so they DO need their
    # ordering reapplied after .annotate() strips it (Django #32811).
    ordering = queryset.model._meta.ordering or ()
    if any(isinstance(f, str) and f.lstrip('-') in ('sort_path', 'path') for f in ordering):
        return queryset

    # TODO: Remove in NetBox v5.0 (see _is_mptt_model). Plugins may still use MPTT
    # via the generic bulk views, so keep exempting MPTT-based models for now.
    if _is_mptt_model(queryset.model):
        return queryset

    if queryset.ordered:
        return queryset

    ordering = queryset.model._meta.ordering
    return queryset.order_by(*ordering)
