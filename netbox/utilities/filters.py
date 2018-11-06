import django_filters


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
            return super(NullableCharFieldFilter, self).filter(qs, value)
        qs = self.get_method(qs)(**{'{}__isnull'.format(self.name): True})
        return qs.distinct() if self.distinct else qs
