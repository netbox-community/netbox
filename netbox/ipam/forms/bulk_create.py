from django import forms
from django.utils.translation import gettext_lazy as _

from utilities.forms.fields import ExpandableIPNetworkField

__all__ = (
    'IPNetworkBulkCreateForm',
)


class IPNetworkBulkCreateForm(forms.Form):
    """
    Pattern form for bulk-creating IP-based objects (addresses, prefixes).
    """
    pattern = ExpandableIPNetworkField(
        label=_('Pattern')
    )
