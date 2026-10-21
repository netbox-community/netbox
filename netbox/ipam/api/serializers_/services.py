from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from ipam.choices import *
from ipam.constants import SERVICE_ASSIGNMENT_MODELS, SERVICE_PORT_MAX, SERVICE_PORT_MIN
from ipam.models import IPAddress, Service, ServiceTemplate
from ipam.utils import legacy_protocol_and_ports
from ipam.validators import validate_port_mappings
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
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


class PortMappingsSerializerMixin(serializers.Serializer):
    """
    Shared port-mapping handling for the Service and ServiceTemplate serializers, including backward
    compatibility for the legacy single-protocol ``protocol``/``ports`` representation.

    Read: alongside the ``port_mappings`` list, a service that uses a single protocol also reports the
    legacy ``protocol`` and ``ports`` fields; a multi-protocol service reports ``null`` for both (it
    cannot be expressed in the old single-protocol format).

    Write: either format is accepted. When the legacy ``protocol``/``ports`` pair is supplied (and
    ``port_mappings`` is not), it is translated into ``port_mappings``. Supplying both together is
    accepted only when the legacy fields agree with what ``port_mappings`` implies (e.g. a full-object
    round-trip that echoes back the read representation); a genuine conflict is rejected as ambiguous.

    Subclassing ``serializers.Serializer`` (rather than a plain mixin) lets DRF's metaclass collect the
    fields declared here into the inheriting serializers.
    """
    port_mappings = PortMappingsField(required=False)

    # Legacy single-protocol fields, retained for backward compatibility. They are read straight off the
    # model's protocol/ports properties (which share these field names), so DRF sources them directly —
    # matching the {"value", "label"} shape every other choice field uses. default=None applies only on
    # write, where validate() consumes them.
    # TODO: Remove protocol/ports in v5.0 along with the legacy handling in validate().
    protocol = ChoiceField(
        choices=ServiceProtocolChoices,
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Deprecated; use port_mappings. Reported only for single-protocol services."),
    )
    ports = serializers.ListField(
        child=serializers.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        required=False,
        allow_null=True,
        default=None,
        help_text=_("Deprecated; use port_mappings. Reported only for single-protocol services."),
    )

    def validate(self, data):
        # Consume the legacy fields and translate them into port_mappings *before* calling super(),
        # which instantiates the model (via full_clean()) and would choke on these now-nonexistent kwargs.
        legacy_protocol = data.pop('protocol', None)
        legacy_ports = data.pop('ports', None)
        # protocol/ports carry default=None, so an omitted field arrives as None; an explicitly-supplied
        # value (including a falsy ports=[]) is a legacy write and must be handled — checking `is not None`
        # rather than truthiness so an intentional empty list isn't silently dropped.
        if legacy_protocol is not None or legacy_ports is not None:
            # `port_mappings` and `protocol`/`ports` are mutually exclusive as *representations*, but a
            # full-object round-trip (GET then PUT/PATCH) legitimately resubmits port_mappings alongside
            # the legacy protocol/ports the read emitted. Only reject a genuine *conflict*: when the legacy
            # fields agree with what port_mappings already implies they're merely redundant, so accept the
            # request and let port_mappings win.
            if 'port_mappings' in data:
                expected_protocol, expected_ports = legacy_protocol_and_ports(data['port_mappings'])
                protocol_agrees = legacy_protocol is None or legacy_protocol == expected_protocol
                ports_agree = legacy_ports is None or sorted(legacy_ports) == (expected_ports or [])
                if not (protocol_agrees and ports_agree):
                    raise serializers.ValidationError(_(
                        "Specify either 'port_mappings' or the deprecated 'protocol'/'ports' fields, not both."
                    ))
                return super().validate(data)
            # The old API accepted an empty ports list (the ArrayField had no minimum length); the new
            # model requires at least one mapping. Report that directly — both fields may have been
            # supplied, so the "both are required" message below would be misleading.
            if legacy_ports == []:
                raise serializers.ValidationError(
                    {'ports': _("At least one port mapping is required.")}
                )
            # The legacy API let either field be updated on its own (e.g. a PATCH that adjusts only the
            # port list). Preserve that by backfilling the omitted field from the instance's current
            # single-protocol representation.
            if not (legacy_protocol and legacy_ports):
                legacy_protocol = legacy_protocol or (self.instance.protocol if self.instance else None)
                if legacy_ports is None:
                    legacy_ports = self.instance.ports if self.instance else None
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


class ServiceTemplateSerializer(PortMappingsSerializerMixin, PrimaryModelSerializer):

    class Meta:
        model = ServiceTemplate
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'port_mappings', 'protocol', 'ports', 'description',
            'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'port_mappings', 'description')


class ServiceSerializer(PortMappingsSerializerMixin, PrimaryModelSerializer):
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
