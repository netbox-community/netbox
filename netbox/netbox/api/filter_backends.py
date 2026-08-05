from django.db.models import F
from rest_framework import filters

__all__ = (
    'OrderingFilter',
)


class OrderingFilter(filters.OrderingFilter):
    """
    Extends DRF's OrderingFilter to sort null values last irrespective of the sort direction, and to
    append a stable tiebreaker so that paginating through tied rows cannot skip or repeat them.
    (PostgreSQL sorts nulls first when ordering descending, which pushes rows with no value to the
    top of a descending sort.)

    A viewset may map a field name to a query expression via `ordering_expressions` to order by
    something other than the named column; this is used where the value presented to the user is
    computed rather than stored.
    """
    def filter_queryset(self, request, queryset, view):
        if not (ordering := self.get_ordering(request, queryset, view)):
            return queryset

        expressions = getattr(view, 'ordering_expressions', {})
        terms = []
        for term in ordering:
            if descending := term.startswith('-'):
                term = term[1:]
            expression = expressions[term] if term in expressions else F(term)
            terms.append(
                expression.desc(nulls_last=True) if descending else expression.asc(nulls_last=True)
            )

        return queryset.order_by(*terms, 'pk')
