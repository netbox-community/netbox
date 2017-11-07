from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from netaddr import IPNetwork, AddrFormatError


#
# Form fields
#

class IPFormField(forms.Field):
    default_error_messages = {
        'invalid': "Enter a valid IPv4 or IPv6 address (with CIDR mask).",
    }

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPNetwork):
            return value

        # Ensure that a subnet mask has been specified. This prevents IPs from defaulting to a /32 or /128.
        if len(value.split('/')) != 2:
            raise ValidationError('CIDR mask (e.g. /24) is required.')

        try:
            return IPNetwork(value)
        except AddrFormatError:
            raise ValidationError("Please specify a valid IPv4 or IPv6 address.")
