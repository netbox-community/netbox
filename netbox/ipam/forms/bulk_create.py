from django import forms

from utilities.forms import BootstrapMixin, ExpandableIPAddressField

__all__ = (
    'IPAddressBulkCreateForm',
)


class IPAddressBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableIPAddressField(
        label='Address pattern'
    )
