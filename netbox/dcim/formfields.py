from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from netaddr import EUI, AddrFormatError


#
# Form fields
#

class MACAddressFormField(forms.Field):
    default_error_messages = {
        'invalid': "Enter a valid MAC address.",
    }

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, EUI):
            return value

        try:
            return EUI(value, version=48)
        except AddrFormatError:
            raise ValidationError("Please specify a valid MAC address.")
