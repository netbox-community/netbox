from netaddr import IPNetwork

from django.core.exceptions import ValidationError
from django.db import models

from .formfields import IPFormField
from .lookups import (
    EndsWith, IEndsWith, IRegex, IStartsWith, NetContained, NetContainedOrEqual, NetContains, NetContainsOrEquals,
    NetHost, Regex, StartsWith,
)


def prefix_validator(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError("{} is not a valid prefix. Did you mean {}?".format(prefix, prefix.cidr))


class BaseIPField(models.Field):

    def python_type(self):
        return IPNetwork

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value
        try:
            return IPNetwork(value)
        except ValueError as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        if not value:
            return None
        return str(self.to_python(value))

    def form_class(self):
        return IPFormField

    def formfield(self, **kwargs):
        defaults = {'form_class': self.form_class()}
        defaults.update(kwargs)
        return super(BaseIPField, self).formfield(**defaults)


class IPNetworkField(BaseIPField):
    """
    IP prefix (network and mask)
    """
    description = "PostgreSQL CIDR field"
    default_validators = [prefix_validator]

    def db_type(self, connection):
        return 'cidr'


IPNetworkField.register_lookup(EndsWith)
IPNetworkField.register_lookup(IEndsWith)
IPNetworkField.register_lookup(StartsWith)
IPNetworkField.register_lookup(IStartsWith)
IPNetworkField.register_lookup(Regex)
IPNetworkField.register_lookup(IRegex)
IPNetworkField.register_lookup(NetContained)
IPNetworkField.register_lookup(NetContainedOrEqual)
IPNetworkField.register_lookup(NetContains)
IPNetworkField.register_lookup(NetContainsOrEquals)
IPNetworkField.register_lookup(NetHost)


class IPAddressField(BaseIPField):
    """
    IP address (host address and mask)
    """
    description = "PostgreSQL INET field"

    def db_type(self, connection):
        return 'inet'


IPAddressField.register_lookup(EndsWith)
IPAddressField.register_lookup(IEndsWith)
IPAddressField.register_lookup(StartsWith)
IPAddressField.register_lookup(IStartsWith)
IPAddressField.register_lookup(Regex)
IPAddressField.register_lookup(IRegex)
IPAddressField.register_lookup(NetContained)
IPAddressField.register_lookup(NetContainedOrEqual)
IPAddressField.register_lookup(NetContains)
IPAddressField.register_lookup(NetContainsOrEquals)
IPAddressField.register_lookup(NetHost)
