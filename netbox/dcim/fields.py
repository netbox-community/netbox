from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from netaddr import AddrFormatError, EUI, eui64_unix_expanded, mac_unix_expanded

from .lookups import PathContains

__all__ = (
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

class MACAddressField(models.Field):
    description = "PostgreSQL MAC Address field"

    def python_type(self):
        return EUI

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value
        if type(value) is str:
            value = value.replace(' ', '')
        try:
            return EUI(value, version=48, dialect=mac_unix_expanded_uppercase)
        except AddrFormatError:
            raise ValidationError(_("Invalid MAC address format: {value}").format(value=value))

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
            raise ValidationError(_("Invalid WWN format: {value}").format(value=value))

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
