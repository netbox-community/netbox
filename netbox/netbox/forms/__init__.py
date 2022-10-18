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


class SearchForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        label='Search',
        widget=forms.TextInput(
            attrs={
                'hx-get': '',
                'hx-target': '#search_results',
                'hx-trigger': 'keyup[target.value.length >= 3] changed delay:500ms',
            }
        )
    )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['obj_types'].choices = search_backend.get_object_types()
