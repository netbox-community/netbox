from __future__ import unicode_literals

import itertools

import django_filters
from django import forms
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
    """
    Allow matching on null field values by passing a special string used to signify NULL.
    """
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

    def __init__(self, null_value=0, null_label='-- None --', *args, **kwargs):
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
