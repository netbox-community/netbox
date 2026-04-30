import re

from django import forms
from django.utils.translation import gettext as _

from .mixins import ChangelogMessageMixin

__all__ = (
    'BulkRenameForm',
)


class BulkRenameForm(ChangelogMessageMixin, forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField(
        strip=False
    )
    replace = forms.CharField(
        strip=False,
        required=False
    )
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use regular expressions')
    )

    def clean(self):
        super().clean()

        # Validate regular expression in "find" field
        if self.cleaned_data['use_regex']:
            try:
                re.compile(self.cleaned_data['find'])
            except re.error:
                raise forms.ValidationError({
                    'find': "Invalid regular expression"
                })
