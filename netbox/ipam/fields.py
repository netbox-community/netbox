from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from netaddr import AddrFormatError, IPNetwork

from . import lookups, validators
from .formfields import IPNetworkFormField

__all__ = (
    'ASNField',
    'IPAddressField',
    'IPNetworkField',
)

# BGP ASN bounds
BGP_ASN_MIN = 1
BGP_ASN_MAX = 2**32 - 1


class BaseIPField(models.Field):

    def python_type(self):
        return IPNetwork

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value
        try:
            # Always return a netaddr.IPNetwork object. (netaddr.IPAddress does not provide a mask.)
            return IPNetwork(value)
        except AddrFormatError:
            raise ValidationError("Invalid IP address format: {}".format(value))
        except (TypeError, ValueError) as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        if not value:
            return None
        if isinstance(value, list):
            return [str(self.to_python(v)) for v in value]
        return str(self.to_python(value))

    def form_class(self):
        return IPNetworkFormField

    def formfield(self, **kwargs):
        defaults = {'form_class': self.form_class()}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class IPNetworkField(BaseIPField):
    """
    IP prefix (network and mask)
    """
    description = "PostgreSQL CIDR field"
    default_validators = [validators.prefix_validator]

    def db_type(self, connection):
        return 'cidr'


IPNetworkField.register_lookup(lookups.IExact)
IPNetworkField.register_lookup(lookups.EndsWith)
IPNetworkField.register_lookup(lookups.IEndsWith)
IPNetworkField.register_lookup(lookups.StartsWith)
IPNetworkField.register_lookup(lookups.IStartsWith)
IPNetworkField.register_lookup(lookups.Regex)
IPNetworkField.register_lookup(lookups.IRegex)
IPNetworkField.register_lookup(lookups.NetContained)
IPNetworkField.register_lookup(lookups.NetContainedOrEqual)
IPNetworkField.register_lookup(lookups.NetContains)
IPNetworkField.register_lookup(lookups.NetContainsOrEquals)
IPNetworkField.register_lookup(lookups.NetFamily)
IPNetworkField.register_lookup(lookups.NetMaskLength)


class IPAddressField(BaseIPField):
    """
    IP address (host address and mask)
    """
    description = "PostgreSQL INET field"

    def db_type(self, connection):
        return 'inet'


IPAddressField.register_lookup(lookups.IExact)
IPAddressField.register_lookup(lookups.EndsWith)
IPAddressField.register_lookup(lookups.IEndsWith)
IPAddressField.register_lookup(lookups.StartsWith)
IPAddressField.register_lookup(lookups.IStartsWith)
IPAddressField.register_lookup(lookups.Regex)
IPAddressField.register_lookup(lookups.IRegex)
IPAddressField.register_lookup(lookups.NetContained)
IPAddressField.register_lookup(lookups.NetContainedOrEqual)
IPAddressField.register_lookup(lookups.NetContains)
IPAddressField.register_lookup(lookups.NetContainsOrEquals)
IPAddressField.register_lookup(lookups.NetHost)
IPAddressField.register_lookup(lookups.NetIn)
IPAddressField.register_lookup(lookups.NetHostContained)
IPAddressField.register_lookup(lookups.NetFamily)
IPAddressField.register_lookup(lookups.NetMaskLength)


class ASNField(models.BigIntegerField):
    description = "32-bit ASN field"
    default_validators = [
        MinValueValidator(BGP_ASN_MIN),
        MaxValueValidator(BGP_ASN_MAX),
    ]

    def formfield(self, **kwargs):
        defaults = {
            'min_value': BGP_ASN_MIN,
            'max_value': BGP_ASN_MAX,
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)
