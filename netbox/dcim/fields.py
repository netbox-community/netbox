from netaddr import EUI, mac_unix_expanded

from django.core.exceptions import ValidationError
from django.db import models

from .formfields import MACAddressFormField

class mac_unix_expanded_uppercase(mac_unix_expanded):
    word_fmt = '%.2X'


class MACAddressField(models.Field):
    description = "PostgreSQL MAC Address field"

    def python_type(self):
        return EUI

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value
        try:
            return EUI(value, dialect=mac_unix_expanded_uppercase)
        except ValueError as e:
            raise ValidationError(e)

    def db_type(self, connection):
        return 'macaddr'

    def get_prep_value(self, value):
        if not value:
            return None
        return str(self.to_python(value))

    def form_class(self):
        return MACAddressFormField

    def formfield(self, **kwargs):
        defaults = {'form_class': self.form_class()}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)
