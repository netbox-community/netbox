from django.db.models import Count, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce

from netbox.models.ltree import LtreeManager

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


def reapply_model_ordering(queryset: QuerySet) -> QuerySet:
    """
    Reapply model-level ordering in case it has been lost through .annotate().
    https://code.djangoproject.com/ticket/32811
    """
    # Hierarchical (ltree) models are exempt; their default ordering by `sort_path`/`path`
    # must not be clobbered by .annotate(). Use caution when annotating these querysets.
    # Use `managers` (not `local_managers`): the LtreeManager is declared on the abstract
    # NestedLtreeGroupModel base, so concrete subclasses inherit it via the MRO rather than
    # holding it in their own `local_managers`.
    if any(isinstance(manager, LtreeManager) for manager in queryset.model._meta.managers):
        return queryset
    if queryset.ordered:
        return queryset

    ordering = queryset.model._meta.ordering
    return queryset.order_by(*ordering)
