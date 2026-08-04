from functools import cache

import django_filters
from django.db.models import Q

from .models import Tag

__all__ = (
    'MissingKeyAwareFilterMixin',
    'TagFilter',
    'TagIDFilter',
    'missing_key_aware_filter_factory',
)


class MissingKeyAwareFilterMixin:
    """
    Treat a JSON key which is absent as equivalent to one holding a null value when negating a
    lookup: an object with no value for a custom field must match "is not x" however that absence
    is stored.

    Django compiles `exclude(custom_field_data__foo='x')` to a bare `NOT (data -> 'foo' = 'x')`.
    A row which does not carry the key at all yields SQL NULL there, so the negation evaluates to
    NULL and Postgres discards the row. A row holding a JSON null fares no better under any of the
    text lookups (icontains, istartswith, etc.), which compare `data ->> 'foo'` and so are NULL for
    a JSON null as well.

    Both states are common: custom field data is no longer provisioned onto every object when a
    field is created (see CustomField.populate_initial_data()), leaving newer objects without the
    key, while objects provisioned before that change -- and those created through the UI or REST
    API, which record a null for each unset field -- hold an explicit null. Neither may be dropped.

    Only negated filters are affected; for others this is inert.

    Two constraints on where this may be mixed in, both satisfied by every filter class
    CustomField.to_filter() can select:

    * The negated path reimplements MultipleChoiceFilter.filter() rather than delegating to it, so
      any custom filter() on the base class is bypassed when the filter is negated. Do not mix this
      into a class which overrides filter() (e.g. MultiValueMACAddressFilter,
      MultiValueContentTypeFilter).
    * `conjoined` is not honored: multiple values are always OR'ed before negation.
    """
    def filter(self, qs, value):
        if not self.exclude or not value:
            return super().filter(qs, value)

        # Rebuild the positive predicate and negate it explicitly, admitting rows which hold no
        # value for the field. `<key>__isnull` matches only a missing key and `<key>=None` only a
        # JSON null, so together they widen the result set by exactly the rows Django would
        # otherwise drop.
        q = Q()
        for v in set(value):
            q |= Q(**self.get_filter_predicate(v))
        qs = qs.filter(
            ~q |
            Q(**{f'{self.field_name}__isnull': True}) |
            Q(**{self.field_name: None})
        )

        return qs.distinct() if self.distinct else qs


@cache
def missing_key_aware_filter_factory(filter_class):
    """
    Return a subclass of the given filter class which treats an absent JSON key as equivalent to a
    null one when negated. Results are cached so that each filter class yields a single stable
    subclass.
    """
    return type(
        f'MissingKeyAware{filter_class.__name__}',
        (MissingKeyAwareFilterMixin, filter_class),
        {}
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
