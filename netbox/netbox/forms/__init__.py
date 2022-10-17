from django import forms
from django.utils.translation import gettext as _

from netbox.search import LookupTypes
from netbox.search.backends import search_backend
from utilities.forms import BootstrapMixin, StaticSelect, StaticSelectMultiple

from .base import *

LOOKUP_CHOICES = (
    ('', _('Partial match')),
    (LookupTypes.EXACT, _('Exact match')),
    (LookupTypes.STARTSWITH, _('Starts with')),
    (LookupTypes.ENDSWITH, _('Ends with')),
)


def build_options(choices):
    options = [{"label": choices[0][1], "items": []}]

    for label, choices in choices[1:]:
        items = []

        for value, choice_label in choices:
            items.append({"label": choice_label, "value": value})

        options.append({"label": label, "items": items})
    return options


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(label='Search')
    obj_types = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label='Object type(s)',
        widget=StaticSelectMultiple()
    )
    lookup = forms.ChoiceField(
        choices=LOOKUP_CHOICES,
        initial=LookupTypes.PARTIAL,
        required=False,
        widget=StaticSelect()
    )

    options = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['obj_types'].choices = search_backend.get_object_types()

    def get_options(self):
        if not self.options:
            self.options = build_options(search_backend.get_object_types())

        return self.options
