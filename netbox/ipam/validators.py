from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_port_mappings(mappings):
    """
    Validate a normalized list of service port mappings, i.e. dicts of the form
    ``{'protocol': <str>, 'ports': [<int>, ...]}``. Ensures each protocol is specified only once and
    that every port falls within the permitted range. Raises a ``ValidationError`` describing the first
    problem found.

    Shared by the model form field (``PortMappingField``) and the REST API serializers so both enforce
    identical rules.
    """
    # Imported lazily to avoid a circular import during settings load (this module is imported by
    # ipam.models, and ipam.constants pulls in ipam.choices, which reads settings.FIELD_CHOICES).
    from ipam.constants import SERVICE_PORT_MAX, SERVICE_PORT_MIN

    seen_protocols = set()
    for mapping in mappings:
        protocol = mapping.get('protocol')
        ports = mapping.get('ports') or []
        if protocol in seen_protocols:
            raise ValidationError(
                _("Duplicate protocol: {protocol}. Each protocol may be specified only once.").format(
                    protocol=protocol
                )
            )
        seen_protocols.add(protocol)
        if not ports:
            raise ValidationError(
                _("At least one port is required for protocol {protocol}.").format(protocol=protocol)
            )
        for port in ports:
            if not SERVICE_PORT_MIN <= port <= SERVICE_PORT_MAX:
                raise ValidationError(
                    _("Port {port} is not within the permitted range ({min}-{max}).").format(
                        port=port, min=SERVICE_PORT_MIN, max=SERVICE_PORT_MAX
                    )
                )


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
