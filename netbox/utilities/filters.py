from __future__ import unicode_literals

import django_filters
import itertools

from django import forms
from django.db.models import Q
from django.utils.encoding import force_text


#
# Filters
#

class NumericInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """
    Filters for a set of numeric values. Example: id__in=100,200,300
    """
    pass


class NullableCharFieldFilter(django_filters.CharFilter):
    null_value = 'NULL'

    def filter(self, qs, value):
        if value != self.null_value:
            return super(NullableCharFieldFilter, self).filter(qs, value)
        qs = self.get_method(qs)(**{'{}__isnull'.format(self.name): True})
        return qs.distinct() if self.distinct else qs


class NullableModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    This field operates like a normal ModelMultipleChoiceField except that it allows for one additional choice which is
    used to represent a value of Null. This is accomplished by creating a new iterator which first yields the null
    choice before entering the queryset iterator, and by ignoring the null choice during cleaning. The effect is similar
    to defining a MultipleChoiceField with:

        choices = [(0, 'None')] + [(x.id, x) for x in Foo.objects.all()]

    However, the above approach forces immediate evaluation of the queryset, which can cause issues when calculating
    database migrations.
    """
    iterator = forms.models.ModelChoiceIterator

    def __init__(self, null_value=0, null_label='None', *args, **kwargs):
        self.null_value = null_value
        self.null_label = null_label
        super(NullableModelMultipleChoiceField, self).__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        # Prepend the null choice to the queryset iterator
        return itertools.chain(
            [(self.null_value, self.null_label)],
            self.iterator(self),
        )
    choices = property(_get_choices, forms.ChoiceField._set_choices)

    def clean(self, value):
        # Strip all instances of the null value before cleaning
        if value is not None:
            stripped_value = [x for x in value if x != force_text(self.null_value)]
        else:
            stripped_value = value
        super(NullableModelMultipleChoiceField, self).clean(stripped_value)
        return value


class NullableModelMultipleChoiceFilter(django_filters.ModelMultipleChoiceFilter):
    """
    This class extends ModelMultipleChoiceFilter to accept an additional value which implies "is null". The default
    queryset filter argument is:

        .filter(fieldname=value)

    When filtering by the value representing "is null" ('0' by default) the argument is modified to:

        .filter(fieldname__isnull=True)
    """
    field_class = NullableModelMultipleChoiceField

    def __init__(self, *args, **kwargs):
        self.null_value = kwargs.get('null_value', 0)
        super(NullableModelMultipleChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        value = value or ()  # Make sure we have an iterable

        if self.is_noop(qs, value):
            return qs

        # Even though not a noop, no point filtering if empty
        if not value:
            return qs

        q = Q()
        for v in set(value):
            # Filtering by "is null"
            if v == force_text(self.null_value):
                arg = {'{}__isnull'.format(self.name): True}
            # Filtering by a related field (e.g. slug)
            elif self.field.to_field_name is not None:
                arg = {'{}__{}'.format(self.name, self.field.to_field_name): v}
            # Filtering by primary key (default)
            else:
                arg = {self.name: v}
            if self.conjoined:
                qs = self.get_method(qs)(**arg)
            else:
                q |= Q(**arg)
        if self.distinct:
            return self.get_method(qs)(q).distinct()

        return self.get_method(qs)(q)
