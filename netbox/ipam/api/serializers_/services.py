from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS, SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.models import IPAddress, Service, ServiceTemplate
from ipam.validators import legacy_protocol_and_ports, validate_port_mappings
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import PrimaryModelSerializer

from .ip import IPAddressSerializer

__all__ = (
    'ServiceSerializer',
    'ServiceTemplateSerializer',
)


class PortMappingsField(serializers.ListField):
    """
    A service's port mappings as a flat list of ``protocol/port`` strings (e.g. ``["tcp/80", "udp/53"]``),
    matching how they are stored. Each entry is validated (and normalized) on write.
    """
    child = serializers.CharField()

    def to_internal_value(self, data):
        mappings = super().to_internal_value(data)
        try:
            return validate_port_mappings(mappings)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)


# Legacy single-protocol fields, retained on the serializers for backward compatibility. Declared via
# factories (rather than on the shared mixin) because DRF's serializer metaclass only collects declared
# fields from the class itself and other serializers — not from a plain mixin. default=None keeps them
# from being sourced off the (now nonexistent) model attributes; the real values are filled in by
# PortMappingsSerializerMixin.to_representation().
# TODO: Remove in v5.0 along with the legacy handling in PortMappingsSerializerMixin.
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

    Write: either format is accepted, but not both in the same request. When the legacy
    ``protocol``/``ports`` pair is supplied (and ``port_mappings`` is not), it is translated into
    ``port_mappings``; supplying both formats together is rejected as ambiguous.
    """

    def validate(self, data):
        # Consume the legacy fields and translate them into port_mappings *before* calling super(),
        # which instantiates the model (via full_clean()) and would choke on these now-nonexistent kwargs.
        legacy_protocol = data.pop('protocol', None)
        legacy_ports = data.pop('ports', None)
        legacy_supplied = legacy_protocol is not None or legacy_ports is not None
        if legacy_supplied:
            # The two formats are mutually exclusive. Rather than silently dropping one when they conflict,
            # reject the request so the caller picks a single representation.
            if 'port_mappings' in data:
                raise serializers.ValidationError(_(
                    "Specify either 'port_mappings' or the deprecated 'protocol'/'ports' fields, not both."
                ))
            # The legacy API let either field be updated on its own (e.g. a PATCH that adjusts only the
            # port list). Preserve that by backfilling the omitted field from the instance's current
            # single-protocol representation.
            if not (legacy_protocol and legacy_ports):
                existing_protocol, existing_ports = (
                    legacy_protocol_and_ports(self.instance.port_mappings) if self.instance else (None, None)
                )
                legacy_protocol = legacy_protocol or existing_protocol
                if legacy_ports is None:
                    legacy_ports = existing_ports
            # If the pair still can't be resolved — a create, or an existing multi-protocol service that
            # has no single-protocol form — the request can't be expressed in the legacy format.
            if not (legacy_protocol and legacy_ports):
                raise serializers.ValidationError(_(
                    "Both 'protocol' and 'ports' are required when writing via the deprecated legacy "
                    "format; use port_mappings instead."
                ))
            try:
                data['port_mappings'] = validate_port_mappings(
                    [f'{legacy_protocol}/{port}' for port in legacy_ports]
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'ports': exc.messages})

        return super().validate(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Populate the legacy single-protocol representation for backward compatibility. Skipped in
        # brief mode, where these fields are not exposed. The empty and multi-protocol cases are kept
        # distinct: an empty service reports ports=[] (as the old API always did), whereas a service
        # with multiple protocols reports ports=null to signal "not representable in the legacy format;
        # use port_mappings".
        if 'protocol' in self.fields and 'ports' in self.fields:
            data['protocol'], data['ports'] = legacy_protocol_and_ports(instance.port_mappings)

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
