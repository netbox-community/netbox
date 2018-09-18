from __future__ import unicode_literals

from netaddr import AddrFormatError, EUI, mac_unix_expanded

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class ASNField(models.BigIntegerField):
    description = "32-bit ASN field"
    default_validators = [
        MinValueValidator(1),
        MaxValueValidator(4294967295),
    ]


class mac_unix_expanded_uppercase(mac_unix_expanded):
    word_fmt = '%.2X'


class MACAddressField(models.Field):
    description = "PostgreSQL MAC Address field"

    def python_type(self):
        return EUI

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return EUI(value, version=48, dialect=mac_unix_expanded_uppercase)
        except AddrFormatError as e:
            raise ValidationError(e)

    def db_type(self, connection):
        return 'macaddr'

    def get_prep_value(self, value):
        if not value:
            return None
        return str(self.to_python(value))
