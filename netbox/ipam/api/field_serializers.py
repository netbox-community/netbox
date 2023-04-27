from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ipam import models
from netaddr import AddrFormatError, IPNetwork

__all__ = [
    'IPAddressField',
]


#
# IP address field
#

class IPAddressField(serializers.CharField):
    """IPAddressField with mask"""

    default_error_messages = {
        'invalid': _('Enter a valid IPv4 or IPv6 address with optional mask.'),
    }

    def to_internal_value(self, data):
        try:
            return IPNetwork(data)
        except AddrFormatError:
            raise serializers.ValidationError("Invalid IP address format: {}".format(data))
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(e)

    def to_representation(self, value):
        return str(value)
