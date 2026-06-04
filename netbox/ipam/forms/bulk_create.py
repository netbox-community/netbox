from django import forms
from django.utils.translation import gettext_lazy as _

from ipam.constants import VLAN_VID_MAX, VLAN_VID_MIN
from utilities.forms.fields import ExpandableIPNetworkField, NumericArrayField

__all__ = (
    'IPNetworkBulkCreateForm',
    'VLANIDBulkCreateForm',
)


class IPNetworkBulkCreateForm(forms.Form):
    """
    Pattern form for bulk-creating IP-based objects (addresses, prefixes).
    """
    pattern = ExpandableIPNetworkField(
        label=_('Pattern')
    )


class VLANIDBulkCreateForm(forms.Form):
    pattern = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=VLAN_VID_MIN,
            max_value=VLAN_VID_MAX
        ),
        label=_('VLAN IDs'),
        help_text=_(
            'Enter VLAN IDs and ranges separated by commas. '
            'Example: 100,200-210,3100-3299'
        )
    )
