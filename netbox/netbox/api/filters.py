from rest_framework import filters

from netbox.api.fields import RelatedObjectCountField

__all__ = (
    'OrderingFilter',
)


class OrderingFilter(filters.OrderingFilter):
    """
    Extends DRF's OrderingFilter to accept a RelatedObjectCountField as an ordering key only when its annotation has
    been applied to the queryset, which happens only when the field is included in the response.
    """
    def get_default_valid_fields(self, queryset, view, context=None):
        valid_fields = super().get_default_valid_fields(queryset, view, context)
        if hasattr(view, 'get_serializer_class'):
            serializer_class = view.get_serializer_class()
        else:
            serializer_class = view.serializer_class
        count_sources = {
            field.source or field_name
            for field_name, field in serializer_class._declared_fields.items()
            if type(field) is RelatedObjectCountField
        }
        return [
            (source, label) for source, label in valid_fields
            if source not in count_sources or source in queryset.query.annotations
        ]
