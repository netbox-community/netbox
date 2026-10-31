from rest_framework import filters

from netbox.api.fields import RelatedObjectCountField
from utilities.api import get_annotations_for_serializer

__all__ = (
    'OrderingFilter',
)


class OrderingFilter(filters.OrderingFilter):
    """
    Extends DRF's OrderingFilter to annotate a RelatedObjectCountField named by the ordering when the response leaves
    it out, since its annotation is otherwise applied only when the field is included in the response.
    """
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset

        if hasattr(view, 'get_serializer_class'):
            serializer_class = view.get_serializer_class()
        else:
            serializer_class = view.serializer_class
        count_fields = {
            field.source or field_name: field_name
            for field_name, field in serializer_class._declared_fields.items()
            if isinstance(field, RelatedObjectCountField)
        }
        missing = [
            count_fields[source] for source in (term.lstrip('-') for term in ordering)
            if source in count_fields and source not in queryset.query.annotations
        ]
        if missing:
            queryset = queryset.annotate(**get_annotations_for_serializer(serializer_class, fields=missing))

        return queryset.order_by(*ordering)
