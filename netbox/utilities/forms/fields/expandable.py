import re

import netaddr
from django import forms
from django.utils.translation import gettext_lazy as _

from utilities.forms.constants import *
from utilities.forms.utils import expand_alphanumeric_pattern, expand_ipnetwork_pattern

__all__ = (
    'ExpandableIPNetworkField',
    'ExpandableNameField',
)


class ExpandableNameField(forms.CharField):
    """
    A field which allows for numeric range expansion
      Example: 'Gi0/[1-3]' => ['Gi0/1', 'Gi0/2', 'Gi0/3']
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = _(
                "Alphanumeric ranges are supported for bulk creation. Mixed cases and types within a single range are "
                "not supported (example: <code>[ge,xe]-0/0/[0-9]</code>)."
            )

    def to_python(self, value):
        if not value:
            return ''
        if re.search(ALPHANUMERIC_EXPANSION_PATTERN, value):
            return list(expand_alphanumeric_pattern(value))
        return [value]


class ExpandableIPNetworkField(forms.CharField):
    """
    A CharField that expands numeric range patterns in IPv4/IPv6 CIDR notation into multiple entries.

    Examples:
        '192.0.2.[1-254]/32' => ['192.0.2.1/32', '192.0.2.2/32', ...]
        '10.[0-3,10-13].0.0/16' => ['10.0.0.0/16', '10.1.0.0/16', ..., '10.10.0.0/16', ...]
        '2001:db8:[0-f]::/64' => ['2001:db8:0::/64', '2001:db8:1::/64', ...]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = _(
                'Use bracket notation to specify numeric ranges for bulk creation (CIDR required).<br />'
                'Examples: <code>192.0.2.[1-10]/32</code>, <code>10.[0-3,10-13].0.0/16</code>, '
                '<code>2001:db8:[a-f]::/64</code>'
            )

    def to_python(self, value):
        if not value:
            return [value]

        # Replace expansion brackets with a neutral value to get a parseable IP/CIDR
        stripped = re.sub(r'\[[^\]]+\]', '0', value)
        try:
            family = netaddr.IPNetwork(stripped).version
        except (netaddr.AddrFormatError, ValueError):
            return [value]

        if family == 4 and re.search(IP4_EXPANSION_PATTERN, value):
            return list(expand_ipnetwork_pattern(value, 4))
        if family == 6 and re.search(IP6_EXPANSION_PATTERN, value):
            return list(expand_ipnetwork_pattern(value.lower(), 6))
        return [value]
