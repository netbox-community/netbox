import re

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator, URLValidator, _lazy_re_compile

from netbox.config import get_config

__all__ = (
    'ColorValidator',
    'EnhancedURLValidator',
    'ExclusionValidator',
    'validate_regex',
)


ColorValidator = RegexValidator(
    regex='^[0-9a-f]{6}$',
    message='Enter a valid hexadecimal RGB color code.',
    code='invalid'
)


class EnhancedURLValidator(URLValidator):
    """
    Extends Django's built-in URLValidator to permit the use of hostnames with no domain extension and enforce allowed
    schemes specified in the configuration.
    """
    fqdn_re = URLValidator.hostname_re + URLValidator.domain_re + URLValidator.tld_re
    host_res = [URLValidator.ipv4_re, URLValidator.ipv6_re, fqdn_re, URLValidator.hostname_re]
    regex = _lazy_re_compile(
        r'^(?:[a-z0-9\.\-\+]*)://'          # Scheme (enforced separately)
        r'(?:\S+(?::\S*)?@)?'               # HTTP basic authentication
        r'(?:' + '|'.join(host_res) + ')'   # IPv4, IPv6, FQDN, or hostname
        r'(?::\d{2,5})?'                    # Port number
        r'(?:[/?#][^\s]*)?'                 # Path
        r'\Z', re.IGNORECASE)
    schemes = None

    def __call__(self, value):
        if self.schemes is None:
            # We can't load the allowed schemes until the configuration has been initialized
            self.schemes = get_config().ALLOWED_URL_SCHEMES
        return super().__call__(value)


class ExclusionValidator(BaseValidator):
    """
    Ensure that a field's value is not equal to any of the specified values.
    """
    message = 'This value may not be %(show_value)s.'

    def compare(self, a, b):
        return a in b


def validate_regex(value):
    """
    Checks that the value is a valid regular expression. (Don't confuse this with RegexValidator, which *uses* a regex
    to validate a value.)
    """
    try:
        re.compile(value)
    except re.error:
        raise ValidationError(f"{value} is not a valid regular expression.")
