from django import forms
from django.core.exceptions import ValidationError
from netaddr import IPAddress, IPNetwork, AddrFormatError


#
# Form fields
#

class IPAddressFormField(forms.Field):
    default_error_messages = {
        'invalid': "Enter a valid IPv4 or IPv6 address (without a mask).",
    }

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPAddress):
            return value

        try:
            return IPAddress(value)
        except ValueError:
            raise ValidationError('This field requires an IP address without a mask.')
        except AddrFormatError:
            raise ValidationError("Please specify a valid IPv4 or IPv6 address.")


class IPNetworkFormField(forms.Field):
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
