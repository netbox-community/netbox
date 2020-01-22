from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address
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

        # netaddr is a bit too liberal with what it accepts as a valid IP address. For example, '1.2.3' will become
        # IPAddress('1.2.0.3'). Here, we employ Django's built-in IPv4 and IPv6 address validators as a sanity check.
        try:
            validate_ipv4_address(value)
        except ValidationError:
            try:
                validate_ipv6_address(value)
            except ValidationError:
                raise ValidationError("Invalid IPv4/IPv6 address format: {}".format(value))

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
