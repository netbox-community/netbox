from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


def split_port_mapping(mapping):
    """
    Split a ``protocol/port`` string (e.g. ``'tcp/80'``) into its ``(protocol, port)`` parts. A missing
    separator or port yields an empty string for that part, leaving validation to report the problem.
    """
    protocol, _sep, port = mapping.partition('/')
    return protocol, port


def group_port_mappings(mappings):
    """
    Group a flat ``['tcp/80', 'tcp/443', 'udp/53']`` list into an ordered ``{protocol: [ports]}`` dict,
    preserving first-seen protocol order. Shared by the display property and the form widget so the
    ``protocol/port`` string is parsed in exactly one place.
    """
    grouped = {}
    for mapping in mappings:
        protocol, port = split_port_mapping(mapping)
        grouped.setdefault(protocol, []).append(port)
    return grouped


def validate_port_mappings(mappings):
    """
    Validate a list of service port mappings, i.e. ``protocol/port`` strings such as ``'tcp/80'``.
    Ensures each entry is well-formed, uses a known protocol, falls within the permitted port range,
    and is not duplicated. Raises a ``ValidationError`` describing the first problem found.

    Returns the list in a canonical, normalized form (integer ports, so ``'tcp/080'`` becomes
    ``'tcp/80'``); callers should persist the returned value so every entry path stores identical
    strings and remains matchable by the port filters. Shared by the model (``ServiceBase.clean()``),
    the model form field (``PortMappingField``), the CSV import form, and the REST API serializers so
    all paths enforce identical rules.
    """
    # Imported lazily to avoid a circular import during settings load (this module is imported by
    # ipam.models, and ipam.constants pulls in ipam.choices, which reads settings.FIELD_CHOICES).
    from ipam.choices import ServiceProtocolChoices
    from ipam.constants import SERVICE_PORT_MAX, SERVICE_PORT_MIN

    valid_protocols = ServiceProtocolChoices.values()
    seen = set()
    normalized_mappings = []
    for mapping in mappings:
        protocol, port = split_port_mapping(mapping)
        if not port:
            raise ValidationError(
                _("Invalid port mapping '{mapping}'. Expected format protocol/port (e.g. tcp/80).").format(
                    mapping=mapping
                )
            )
        if protocol not in valid_protocols:
            raise ValidationError(_("Invalid protocol: {protocol}").format(protocol=protocol))
        try:
            port_number = int(port)
        except ValueError:
            raise ValidationError(_("Invalid port number: {port}").format(port=port))
        if not SERVICE_PORT_MIN <= port_number <= SERVICE_PORT_MAX:
            raise ValidationError(
                _("Port {port} is not within the permitted range ({min}-{max}).").format(
                    port=port_number, min=SERVICE_PORT_MIN, max=SERVICE_PORT_MAX
                )
            )
        # Normalize the port to an integer so e.g. tcp/80 and tcp/080 count as duplicates and are
        # stored identically (leaving the raw string would make tcp/080 invisible to the port filter).
        normalized = f'{protocol}/{port_number}'
        if normalized in seen:
            raise ValidationError(_("Duplicate port mapping: {mapping}").format(mapping=mapping))
        seen.add(normalized)
        normalized_mappings.append(normalized)

    return normalized_mappings


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
