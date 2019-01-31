import django_filters
from django.db.models import Q
from taggit.models import Tag


class NumericInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    Filters for a set of numeric values. Example: id__in=100,200,300
    """
    pass


class NullableCharFieldFilter(django_filters.CharFilter):
    """
    Allow matching on null field values by passing a special string used to signify NULL.
    """
    null_value = 'NULL'

    def filter(self, qs, value):
        if value != self.null_value:
            return super().filter(qs, value)
        qs = self.get_method(qs)(**{'{}__isnull'.format(self.name): True})
        return qs.distinct() if self.distinct else qs


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


class NameSlugSearchFilterSet(django_filters.FilterSet):
    """
    A base class for adding the search method to models which only expose the `name` and `slug` fields
    """
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        )
