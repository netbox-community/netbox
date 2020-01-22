from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator


def prefix_validator(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError("{} is not a valid prefix. Did you mean {}?".format(prefix, prefix.cidr))


class MaxPrefixLengthValidator(BaseValidator):
    message = 'The prefix length must be less than or equal to %(limit_value)s.'
    code = 'max_prefix_length'

    def compare(self, a, b):
        return a.prefixlen > b


class MinPrefixLengthValidator(BaseValidator):
    message = 'The prefix length must be greater than or equal to %(limit_value)s.'
    code = 'min_prefix_length'

    def compare(self, a, b):
        return a.prefixlen < b


DNSValidator = RegexValidator(
    regex='^[0-9A-Za-z._-]+$',
    message='Only alphanumeric characters, hyphens, periods, and underscores are allowed in DNS names',
    code='invalid'
)
