from rest_framework import filters

from netbox.api.fields import RelatedObjectCountField
from utilities.api import get_annotations_for_serializer

__all__ = (
    'OrderingFilter',
)


class OrderingFilter(filters.OrderingFilter):
    """
    Extends DRF's OrderingFilter to order by a RelatedObjectCountField under its field name rather than its source,
    annotating the count when the response leaves it out, since its annotation is otherwise applied only when the field
    is included in the response.
    """
    @staticmethod
    def _get_serializer_class(view):
        if hasattr(view, 'get_serializer_class'):
            return view.get_serializer_class()
        return view.serializer_class

    def _get_count_sources(self, view):
        """Map the name of each RelatedObjectCountField on the view's serializer to its source."""
        return {
            field_name: field.source or field_name
            for field_name, field in self._get_serializer_class(view)._declared_fields.items()
            if isinstance(field, RelatedObjectCountField)
        }

    def get_default_valid_fields(self, queryset, view, context=None):
        field_names = {source: field_name for field_name, source in self._get_count_sources(view).items()}
        return [
            (field_names.get(key, key), label)
            for key, label in super().get_default_valid_fields(queryset, view, context)
        ]

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset

        count_sources = self._get_count_sources(view)
        terms = []
        missing = []
        for term in ordering:
            if isinstance(term, str) and (field_name := term.lstrip('-')) in count_sources:
                source = count_sources[field_name]
                if source not in queryset.query.annotations:
                    missing.append(field_name)
                term = f'-{source}' if term.startswith('-') else source
            terms.append(term)
        if missing:
            serializer_class = self._get_serializer_class(view)
            queryset = queryset.annotate(**get_annotations_for_serializer(serializer_class, fields=missing))

        return queryset.order_by(*terms)
