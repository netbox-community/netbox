from netaddr import IPNetwork, AddrFormatError
import netaddr

from django import forms
from django.core.exceptions import ValidationError

from ipam.models import IPAddress, Prefix


#
# Form fields
#

class AddressFormField(forms.Field):
    default_error_messages = {
        'invalid': "Enter a valid IPv4 or IPv6 address (with CIDR mask).",
    }

    def to_python(self, value):
        if not value:
            return None

        # Ensure that a subnet mask has been specified. This prevents IPs from defaulting to a /32 or /128.
        if len(value.split('/')) != 2:
            raise ValidationError('CIDR mask (e.g. /24) is required.')

        try:
            net = IPNetwork(value)
        except AddrFormatError:
            raise ValidationError("Please specify a valid IPv4 or IPv6 address.")

        ip = IPAddress.objects.filter(address=value)
        if not ip:
            net = IPNetwork(value)
            obj = IPAddress(address=net)
            obj.save()
            return obj
        else:
            return ip[0]
