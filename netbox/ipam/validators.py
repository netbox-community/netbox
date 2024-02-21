from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


def prefix_validator(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError(
            _("{prefix} is not a valid prefix. Did you mean {suggested}?").format(
                prefix=prefix, suggested=prefix.cidr
            )
        )


class MaxPrefixLengthValidator(BaseValidator):
    message = _('The prefix length must be less than or equal to %(limit_value)s.')
    code = 'max_prefix_length'

    def compare(self, a, b):
        return a.prefixlen > b


class MinPrefixLengthValidator(BaseValidator):
    message = _('The prefix length must be greater than or equal to %(limit_value)s.')
    code = 'min_prefix_length'

    def compare(self, a, b):
        return a.prefixlen < b


DNSValidator = RegexValidator(
    regex=r'^([0-9A-Za-z_-]+|\*)(\.[0-9A-Za-z_-]+)*\.?$',
    message=_('Only alphanumeric characters, asterisks, hyphens, periods, and underscores are allowed in DNS names'),
    code='invalid'
)
