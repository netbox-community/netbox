from django import forms
from utilities.forms import BootstrapMixin

from search.backends import default_search_engine

from .base import *


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
    options = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["obj_type"] = forms.ChoiceField(choices=default_search_engine.get_search_choices(), required=False, label='Type')

    def get_options(self):
        if not self.options:
            self.options = build_options(default_search_engine.get_search_choices())

        return self.options
