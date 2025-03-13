import django_filters

from .models import Tag

__all__ = (
    'TagFilter',
    'TagIDFilter',
)


class TagFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=foo&tag=bar), the queryset is filtered
    to objects matching all tags.
    """
    def __init__(self, *args, **kwargs):

        kwargs.setdefault('field_name', 'tags__slug')
        kwargs.setdefault('to_field_name', 'slug')
        kwargs.setdefault('conjoined', True)
        kwargs.setdefault('queryset', Tag.objects.all())

        super().__init__(*args, **kwargs)


class TagIDFilter(django_filters.ModelMultipleChoiceFilter):
    """
    Match on one or more assigned tags. If multiple tags are specified (e.g. ?tag=1&tag=2), the queryset is filtered
    to objects matching all tags.
    """
    def __init__(self, *args, **kwargs):

        kwargs.setdefault('field_name', 'tags__id')
        kwargs.setdefault('to_field_name', 'id')
        kwargs.setdefault('conjoined', True)
        kwargs.setdefault('queryset', Tag.objects.all())

        super().__init__(*args, **kwargs)
