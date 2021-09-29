from django import forms
from netaddr import EUI
from netaddr.core import AddrFormatError

__all__ = (
    'MACAddressField',
)


class MACAddressField(forms.Field):
    widget = forms.CharField
    default_error_messages = {
        'invalid': 'MAC address must be in EUI-48 format',
    }

    def to_python(self, value):
        value = super().to_python(value)

        # Validate MAC address format
        try:
            value = EUI(value.strip())
        except AddrFormatError:
            raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

        return value
