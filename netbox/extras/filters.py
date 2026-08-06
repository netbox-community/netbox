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
    Treat a JSON key which is absent as equivalent to one holding a null value: an object storing
    no value for a custom field must filter identically however that absence is represented.

    Custom field data materializes a key only once a value is assigned to it (see
    CustomField.populate_initial_data()), so an object predating a field carries no key for it at
    all, whereas one whose value has been cleared holds a JSON null. Postgres treats the two
    differently, in two places:

    * Django compiles `exclude(custom_field_data__foo='x')` to a bare `NOT (data -> 'foo' = 'x')`.
      A row which does not carry the key yields SQL NULL there, so the negation evaluates to NULL
      and the row is discarded. A row holding a JSON null fares no better under any of the text
      lookups (icontains, istartswith, etc.), which compare `data ->> 'foo'` and so are NULL for a
      JSON null as well.
    * The null sentinel (`?cf_foo=null`; see FILTERS_NULL_CHOICE_VALUE) asks for the objects holding
      no value. MultipleChoiceFilter.filter() translates it to None and hands it to
      get_filter_predicate(), which builds a lookup matching a JSON null only -- silently omitting
      every object which predates the field.

    Both directions are handled: the sentinel is mapped onto "holds no value" rather than onto a
    predicate of its own, and a negation is built explicitly so that valueless rows are admitted.

    Two constraints on where this may be mixed in, both satisfied by every filter class
    CustomField.to_filter() can select:

    * filter() is reimplemented rather than delegated to, so any custom filter() on the base class
      is bypassed. Do not mix this into a class which overrides filter() (e.g.
      MultiValueMACAddressFilter, MultiValueContentTypeFilter).
      missing_key_aware_filter_factory() rejects such classes.
    * `conjoined` is not honored: multiple values are always OR'ed. Passing it raises TypeError.
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get('conjoined'):
            raise TypeError(
                f"{type(self).__name__} does not support conjoined filtering: multiple values are "
                f"always OR'ed."
            )
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return super().filter(qs, value)

        # `<key>__isnull` matches only a missing key and `<key>=None` only a JSON null, so together
        # they select exactly the objects holding no value. Both are null-safe, which is what makes
        # them usable inside the negation below.
        unset = Q(**{f'{self.field_name}__isnull': True}) | Q(**{self.field_name: None})

        values = set(value)
        match_unset = self.null_value in values
        values.discard(self.null_value)

        q = Q()
        for v in values:
            q |= Q(**self.get_filter_predicate(v))
        if match_unset:
            q |= unset

        if self.exclude:
            # Negate explicitly rather than deferring to exclude(), whose bare NOT discards the
            # rows carrying no key. Those rows are admitted, unless holding no value is itself one
            # of the things being excluded.
            q = ~q if match_unset else ~q | unset

        qs = qs.filter(q)

        return qs.distinct() if self.distinct else qs


@cache
def missing_key_aware_filter_factory(filter_class):
    """
    Return a subclass of the given filter class which treats an absent JSON key as equivalent to a
    null one. Results are cached so that each filter class yields a single stable subclass.

    The class must inherit MultipleChoiceFilter.filter() unmodified: the mixin reimplements it, so a
    filter() of its own (and with it any custom predicate or short-circuit) would be silently
    bypassed, yielding a wrong result set rather than an error.
    """
    if filter_class.filter is not django_filters.MultipleChoiceFilter.filter:
        raise TypeError(
            f"{filter_class.__name__} cannot be made missing-key aware: it defines its own "
            f"filter(), which MissingKeyAwareFilterMixin would bypass."
        )

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
