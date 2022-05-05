from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from netaddr import AddrFormatError, EUI, eui64_unix_expanded, mac_unix_expanded

from ipam.constants import BGP_ASN_MAX, BGP_ASN_MIN
from .lookups import PathContains

__all__ = (
    'ASNField',
    'MACAddressField',
    'PathField',
    'WWNField',
)


class mac_unix_expanded_uppercase(mac_unix_expanded):
    word_fmt = '%.2X'


class eui64_unix_expanded_uppercase(eui64_unix_expanded):
    word_fmt = '%.2X'


#
# Fields
#

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


class MACAddressField(models.Field):
    description = "PostgreSQL MAC Address field"

    def python_type(self):
        return EUI

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return EUI(value, version=48, dialect=mac_unix_expanded_uppercase)
        except AddrFormatError:
            raise ValidationError(f"Invalid MAC address format: {value}")

    def db_type(self, connection):
        return 'macaddr'

    def get_prep_value(self, value):
        if not value:
            return None
        return str(self.to_python(value))


class WWNField(models.Field):
    description = "World Wide Name field"

    def python_type(self):
        return EUI

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return EUI(value, version=64, dialect=eui64_unix_expanded_uppercase)
        except AddrFormatError:
            raise ValidationError(f"Invalid WWN format: {value}")

    def db_type(self, connection):
        return 'macaddr8'

    def get_prep_value(self, value):
        if not value:
            return None
        return str(self.to_python(value))


class PathField(ArrayField):
    """
    An ArrayField which holds a set of objects, each identified by a (type, ID) tuple.
    """
    def __init__(self, **kwargs):
        kwargs['base_field'] = models.CharField(max_length=40)
        super().__init__(**kwargs)


PathField.register_lookup(PathContains)
