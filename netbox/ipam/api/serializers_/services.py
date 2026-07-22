from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS, SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.models import IPAddress, Service, ServiceTemplate
from ipam.validators import group_port_mappings, validate_port_mappings
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class PortMappingSerializer(serializers.Serializer):
    """A single protocol and its associated ports, e.g. ``{"protocol": "tcp", "ports": [80, 443]}``."""
    protocol = serializers.ChoiceField(choices=ServiceProtocolChoices)
    ports = serializers.ListField(
        child=serializers.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        allow_empty=False,
    )


@extend_schema_field(PortMappingSerializer(many=True))
class PortMappingsField(serializers.Field):
    """
    Presents a service's port mappings as a grouped list of ``{protocol, ports}`` objects (one entry per
    protocol) in both directions, while the model stores them flat as ``protocol/port`` strings. The
    grouped shape mirrors the legacy single-protocol representation, easing migration.
    """

    def to_representation(self, value):
        return [
            {'protocol': protocol, 'ports': sorted(int(port) for port in ports)}
            for protocol, ports in group_port_mappings(value).items()
        ]

    def to_internal_value(self, data):
        # Validate the grouped structure, then flatten to the model's canonical protocol/port strings
        # (which also merges any repeated protocols and normalizes/deduplicates ports).
        entries = PortMappingSerializer(data=data, many=True)
        entries.is_valid(raise_exception=True)
        mappings = [
            f'{entry["protocol"]}/{port}'
            for entry in entries.validated_data
            for port in entry['ports']
        ]
        try:
            return validate_port_mappings(mappings)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)


# Legacy single-protocol fields, retained on the serializers for backward compatibility. Declared via
# factories (rather than on the shared mixin) because DRF's serializer metaclass only collects declared
# fields from the class itself and other serializers — not from a plain mixin. default=None keeps them
# from being sourced off the (now nonexistent) model attributes; the real values are filled in by
# PortMappingsSerializerMixin.to_representation().
def _legacy_protocol_field():
    return serializers.ChoiceField(
        choices=ServiceProtocolChoices,
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Deprecated; use port_mappings. Reported only for single-protocol services."),
    )


def _legacy_ports_field():
    return serializers.ListField(
        child=serializers.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Deprecated; use port_mappings. Reported only for single-protocol services."),
    )


class PortMappingsSerializerMixin:
    """
    Shared port-mapping handling for the Service and ServiceTemplate serializers, including backward
    compatibility for the legacy single-protocol ``protocol``/``ports`` representation.

    Read: alongside the ``port_mappings`` list, a service that uses a single protocol also reports the
    legacy ``protocol`` and ``ports`` fields; a multi-protocol service reports ``null`` for both (it
    cannot be expressed in the old single-protocol format).

    Write: either format is accepted. ``port_mappings`` takes precedence when supplied; otherwise the
    legacy ``protocol``/``ports`` pair is translated into ``port_mappings``.
    """

    def validate(self, data):
        # Consume the legacy fields and translate them into port_mappings *before* calling super(),
        # which instantiates the model (via full_clean()) and would choke on these now-nonexistent
        # kwargs. port_mappings takes precedence when both formats are supplied.
        legacy_protocol = data.pop('protocol', None)
        legacy_ports = data.pop('ports', None)
        if not data.get('port_mappings') and legacy_protocol and legacy_ports:
            try:
                data['port_mappings'] = validate_port_mappings(
                    [f'{legacy_protocol}/{port}' for port in legacy_ports]
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'ports': exc.messages})

        # Require at least one mapping whenever they're being written (a create, or an update that sets
        # them). A partial update that touches neither format leaves the existing mappings intact.
        writing_mappings = 'port_mappings' in data or not self.partial
        if writing_mappings and not data.get('port_mappings'):
            raise serializers.ValidationError({'port_mappings': _("At least one port mapping is required.")})

        return super().validate(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Populate the legacy single-protocol representation for backward compatibility. Skipped in
        # brief mode, where these fields are not exposed. The empty and multi-protocol cases are kept
        # distinct: an empty service reports ports=[] (as the old API always did), whereas a service
        # with multiple protocols reports ports=null to signal "not representable in the legacy format;
        # use port_mappings".
        if 'protocol' in self.fields and 'ports' in self.fields:
            grouped = group_port_mappings(instance.port_mappings)
            if len(grouped) == 1:
                protocol, ports = next(iter(grouped.items()))
                data['protocol'] = protocol
                data['ports'] = sorted(int(port) for port in ports)
            elif not grouped:
                # No mappings: representable in the legacy format as an empty ports list.
                data['protocol'] = None
                data['ports'] = []
            else:
                # Multiple protocols can't be represented in the old single-protocol format.
                data['protocol'] = None
                data['ports'] = None

        return data


class ServiceTemplateSerializer(PortMappingsSerializerMixin, PrimaryModelSerializer):
    port_mappings = PortMappingsField(required=False)
    protocol = _legacy_protocol_field()
    ports = _legacy_ports_field()

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'port_mappings', 'protocol', 'ports', 'description',
            'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_mappings', 'description')


class ServiceSerializer(PortMappingsSerializerMixin, PrimaryModelSerializer):
    port_mappings = PortMappingsField(required=False)
    protocol = _legacy_protocol_field()
    ports = _legacy_ports_field()
    ipaddresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
        nested=True,
        required=False,
        many=True
    )
    parent_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(SERVICE_ASSIGNMENT_MODELS)
    )
    parent = GFKSerializerField(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'url', 'display_url', 'display', 'parent_object_type', 'parent_object_id', 'parent', 'name',
            'port_mappings', 'protocol', 'ports', 'ipaddresses', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_mappings', 'description')
