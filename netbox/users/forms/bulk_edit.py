from django import forms
from django.utils.translation import gettext as _

from users.models import *
from utilities.forms import BulkEditForm, add_blank_choice

__all__ = (
    'TokenBulkEditForm',
)


class TokenBulkEditForm(BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Token.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    nullable_fields = ('description',)
