from collections.abc import Callable, Sequence

from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.db.models import Model, QuerySet
from strawberry.types import Info
from strawberry_django.optimizer import optimize
from strawberry_django.optimizer import optimizer as optimizer_ctx

__all__ = (
    'build_gfk_prefetch',
    'optimize_prefetch_queryset',
)


def optimize_prefetch_queryset(queryset: QuerySet, info: Info) -> QuerySet:
    """
    Apply strawberry-django's query optimizer to a queryset used inside a GenericForeignKey prefetch.
    """
    if ext := optimizer_ctx.get():
        return ext.optimize(queryset, info)

    return optimize(queryset, info)


def build_gfk_prefetch(
    lookup: str,
    models: Sequence[type[Model]],
) -> Callable[[Info], GenericPrefetch]:
    """
    Return a selection-aware GenericPrefetch for a GenericForeignKey field.

    Each model gets its own queryset, optimized according to the client's GraphQL selection set.
    Querysets are permission-restricted when the manager supports `.restrict()`.
    """

    def prefetch(info: Info) -> GenericPrefetch:
        user = info.context.request.user
        querysets = []

        for model in models:
            qs = model.objects.all()
            if hasattr(qs, 'restrict'):
                qs = qs.restrict(user, 'view')
            querysets.append(optimize_prefetch_queryset(qs, info))

        return GenericPrefetch(lookup, querysets)

    return prefetch
