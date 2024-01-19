from django import forms
from django.utils.translation import gettext_lazy as _

from utilities.forms.fields import ExpandableIPAddressField

__all__ = (
    'IPAddressBulkCreateForm',
)


class IPAddressBulkCreateForm(forms.Form):
    pattern = ExpandableIPAddressField(
        label=_('Address pattern')
    )
