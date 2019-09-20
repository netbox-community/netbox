import re

from django.core.validators import _lazy_re_compile, BaseValidator, URLValidator


class EnhancedURLValidator(URLValidator):
    """
    Extends Django's built-in URLValidator to permit the use of hostnames with no domain extension.
    """
    class AnyURLScheme(object):
        """
        A fake URL list which "contains" all scheme names abiding by the syntax defined in RFC 3986 section 3.1
        """
        def __contains__(self, item):
            if not item or not re.match(r'^[a-z][0-9a-z+\-.]*$', item.lower()):
                return False
            return True

    fqdn_re = URLValidator.hostname_re + URLValidator.domain_re + URLValidator.tld_re
    host_res = [URLValidator.ipv4_re, URLValidator.ipv6_re, fqdn_re, URLValidator.hostname_re]
    regex = _lazy_re_compile(
        r'^(?:[a-z0-9\.\-\+]*)://'          # Scheme (previously enforced by AnyURLScheme or schemes kwarg)
        r'(?:\S+(?::\S*)?@)?'               # HTTP basic authentication
        r'(?:' + '|'.join(host_res) + ')'   # IPv4, IPv6, FQDN, or hostname
        r'(?::\d{2,5})?'                    # Port number
        r'(?:[/?#][^\s]*)?'                 # Path
        r'\Z', re.IGNORECASE)
    schemes = AnyURLScheme()


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
