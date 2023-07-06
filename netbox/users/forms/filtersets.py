from django import forms
from extras.forms.mixins import SavedFiltersMixin
from utilities.forms import FilterForm
from users.models import Token

__all__ = (
    'TokenFilterForm',
)


class TokenFilterForm(SavedFiltersMixin, FilterForm):
    model = Token
