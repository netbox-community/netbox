from django import forms

from utilities.forms import BootstrapMixin
from netbox.constants import SEARCH_TYPE_HIERARCHY


def build_search_choices():
    result = list()
    result.append(('', 'All Objects'))
    for category, items in SEARCH_TYPE_HIERARCHY.items():
        subcategories = list()
        for slug, obj in items.items():
            name = obj['queryset'].model._meta.verbose_name_plural
            name = name[0].upper() + name[1:]
            subcategories.append((slug, name))
        result.append((category, tuple(subcategories)))

    return tuple(result)


OBJ_TYPE_CHOICES = build_search_choices()


def build_options():
    options = [{"label": OBJ_TYPE_CHOICES[0][1], "items": []}]

    for label, choices in OBJ_TYPE_CHOICES[1:]:
        items = []

        for value, choice_label in choices:
            items.append({"label": choice_label, "value": value})

        options.append({"label": label, "items": items})
    return options


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label='Search'
    )
    obj_type = forms.ChoiceField(
        choices=OBJ_TYPE_CHOICES, required=False, label='Type'
    )
    options = build_options()
