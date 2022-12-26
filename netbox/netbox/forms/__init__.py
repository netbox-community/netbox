import re

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
    (LookupTypes.REGEX, _('Regex')),
)


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label=_('Search'),
        widget=forms.TextInput(
            attrs={
                'hx-get': '',
                'hx-target': '#object_list',
                'hx-trigger': 'keyup[target.value.length >= 3] changed delay:500ms',
            }
        )
    )
    obj_types = forms.MultipleChoiceField(
        choices=[],
        required=False,
        label=_('Object type(s)'),
        widget=StaticSelectMultiple()
    )
    lookup = forms.ChoiceField(
        choices=LOOKUP_CHOICES,
        initial=LookupTypes.PARTIAL,
        required=False,
        widget=StaticSelect()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['obj_types'].choices = search_backend.get_object_types()

    def clean(self):

        # Validate regular expressions
        if self.cleaned_data['lookup'] == LookupTypes.REGEX:
            try:
                re.compile(self.cleaned_data['q'])
            except re.error as e:
                raise forms.ValidationError({
                    'q': f'Invalid regular expression: {e}'
                })
