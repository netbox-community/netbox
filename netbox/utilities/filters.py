import django_filters

from django.db.models import Q


class NullableModelMultipleChoiceFilter(django_filters.MultipleChoiceFilter):

    def __init__(self, *args, **kwargs):
        # Convert the queryset to a list of choices prefixed with a "None" option
        queryset = kwargs.pop('queryset')
        self.to_field_name = kwargs.pop('to_field_name', 'pk')
        kwargs['choices'] = [(0, 'None')] + [(getattr(o, self.to_field_name), o) for o in queryset]
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
            # Filtering on NULL
            if v == str(0):
                arg = {'{}__isnull'.format(self.name): True}
            # Filtering on a related field (e.g. slug)
            elif self.to_field_name != 'pk':
                arg = {'{}__{}'.format(self.name, self.to_field_name): v}
            # Filtering on primary key
            else:
                arg = {self.name: v}
            if self.conjoined:
                qs = self.get_method(qs)(**arg)
            else:
                q |= Q(**arg)
        if self.distinct:
            return self.get_method(qs)(q).distinct()

        return self.get_method(qs)(q)
