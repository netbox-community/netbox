from rest_framework import serializers
from netbox.api.serializers import OrganizationalModelSerializer, PrimaryModelSerializer, WritableNestedSerializer
from drf_yasg.utils import swagger_serializer_method

from dcim.api.nested_serializers import (
    NestedDeviceSerializer,
    NestedInterfaceSerializer,
    NestedCableSerializer,
)
from dcim.choices import InterfaceTypeChoices, InterfaceModeChoices
from dcim.models import Interface, Cable, Device
from ipam.api.nested_serializers import NestedPrefixSerializer
from ipam.models import VLAN, Prefix
from tenancy.api.nested_serializers import NestedTenantGroupSerializer, NestedTenantSerializer
from tenancy.models import Tenant as Customer
from utilities.utils import dynamic_import
from netbox.api import ChoiceField, ValidatedModelSerializer, SerializedPKRelatedField, WritableNestedSerializer

from netbox_virtual_circuit_plugin.models import VirtualCircuitVLAN, VirtualCircuit
from circuits.models import Circuit, CircuitTermination


def get_serializer_for_model(model, prefix=''):
    """
    Dynamically resolve and return the appropriate serializer for a model.
    """
    app_name, model_name = model._meta.label.split('.')
    serializer_name = '{}.api.serializers.{}{}Serializer'.format(
        app_name, prefix, model_name
    )

    override_serializer_name = 'vapor.api.serializers.{}VLAN{}Serializer'.format(
        prefix, model_name
    )
    # To extend Circuit model to support tenant field
    if model_name == 'CircuitTermination':
        override_serializer_name = 'vapor.api.serializers.{}Vapor{}Serializer'.format(
            prefix, model_name
        )

    try:
        return dynamic_import(override_serializer_name)
    except AttributeError:
        pass

    try:
        return dynamic_import(serializer_name)
    except AttributeError:
        raise SerializerNotFound(
            "Could not determine serializer for {}.{} with prefix '{}'".format(app_name, model_name, prefix)
        )


class NestedVirtualCircuitSerializer(ValidatedModelSerializer):
    vcid = serializers.ReadOnlyField(source='virtual_circuit.vcid')
    name = serializers.ReadOnlyField(source='virtual_circuit.name')
    status = serializers.ReadOnlyField(source='virtual_circuit.status')
    context = serializers.ReadOnlyField(source='virtual_circuit.context')

    class Meta:
        model = VirtualCircuit
        fields = ['vcid', 'name', 'status', 'context']


class NestedVaporDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')
    tenant = NestedTenantSerializer()

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name', 'tenant']


class NestedVaporVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    prefixes = SerializedPKRelatedField(
        queryset=Prefix.objects.all(),
        serializer=NestedPrefixSerializer,
        required=False,
        many=True,
    )

    virtual_circuit = SerializedPKRelatedField(
        queryset=VirtualCircuitVLAN.objects.all(),
        serializer=NestedVirtualCircuitSerializer,
        pk_field='vlan',
        required=False,
        many=False,
    )

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name', 'prefixes', 'status', 'virtual_circuit']


class NestedVLANInterfaceSerializer(WritableNestedSerializer):
    device = NestedVaporDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    type = ChoiceField(choices=InterfaceTypeChoices, required=False)

    untagged_vlan = NestedVaporVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVaporVLANSerializer,
        required=False,
        many=True,
    )

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'cable', 'type', 'untagged_vlan', 'tagged_vlans']


class NestedVaporCableSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = Cable
        fields = ['id', 'url', 'label', 'status']


class CableTerminationSerializer(serializers.ModelSerializer):
    cable_peer_type = serializers.SerializerMethodField(read_only=True)
    cable_peer = serializers.SerializerMethodField(read_only=True)
    _occupied = serializers.SerializerMethodField(read_only=True)

    def get_cable_peer_type(self, obj):
        if obj._cable_peer is not None:
            return f'{obj._cable_peer._meta.app_label}.{obj._cable_peer._meta.model_name}'
        return None

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_cable_peer(self, obj):
        """
        Return the appropriate serializer for the cable termination model.
        """
        if obj._cable_peer is not None:
            serializer = get_serializer_for_model(obj._cable_peer, prefix='Nested')
            context = {'request': self.context['request']}
            return serializer(obj._cable_peer, context=context).data
        return None

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def get__occupied(self, obj):
        return obj._occupied


class ConnectedEndpointSerializer(ValidatedModelSerializer):
    connected_endpoint_type = serializers.SerializerMethodField(read_only=True)
    connected_endpoint = serializers.SerializerMethodField(read_only=True)
    connected_endpoint_reachable = serializers.SerializerMethodField(read_only=True)

    def get_connected_endpoint_type(self, obj):
        if obj._path is not None and obj._path.destination is not None:
            return f'{obj._path.destination._meta.app_label}.{obj._path.destination._meta.model_name}'
        return None

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_connected_endpoint(self, obj):
        """
        Return the appropriate serializer for the type of connected object.
        """
        if obj._path is not None and obj._path.destination is not None:
            serializer = get_serializer_for_model(obj._path.destination, prefix='Nested')
            context = {'request': self.context['request']}
            return serializer(obj._path.destination, context=context).data
        return None

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def get_connected_endpoint_reachable(self, obj):
        if obj._path is not None:
            return obj._path.is_active
        return None


class CustomerSerializer(PrimaryModelSerializer):
    group = NestedTenantGroupSerializer(required=False)
    devices = NestedDeviceSerializer(required=False, many=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'devices',
        ]


class NestedCircuitSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuit-detail')
    tenant = NestedTenantSerializer()

    class Meta:
        model = Circuit
        fields = ['id', 'url', 'cid', 'tenant', 'status']


class NestedVaporCircuitTerminationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='circuits-api:circuittermination-detail')
    circuit = NestedCircuitSerializer()

    class Meta:
        model = CircuitTermination
        fields = ['id', 'url', 'circuit', 'term_side']


class InterfaceSerializer(PrimaryModelSerializer, CableTerminationSerializer, ConnectedEndpointSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    device = NestedVaporDeviceSerializer()
    type = ChoiceField(choices=InterfaceTypeChoices)
    lag = NestedInterfaceSerializer(required=False, allow_null=True)
    mode = ChoiceField(choices=InterfaceModeChoices, required=False, allow_null=True)
    untagged_vlan = NestedVaporVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVaporVLANSerializer,
        required=False,
        many=True
    )
    cable = NestedVaporCableSerializer(read_only=True)
    count_ipaddresses = serializers.IntegerField(read_only=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'url', 'device', 'name', 'type', 'enabled', 'lag', 'mtu', 'mac_address', 'mgmt_only',
            'description', 'cable', 'cable_peer', 'cable_peer_type', 'mode', 'untagged_vlan', 'tagged_vlans', 'tags',
            'count_ipaddresses', '_occupied', 'mark_connected',
        ]
        ref_name = 'VaporInterfaceSerializer'

    def validate(self, data):

        # All associated VLANs be global or assigned to the parent device's site.
        device = self.instance.device if self.instance else data.get('device')
        for vlan in data.get('tagged_vlans', []):
            if vlan.site not in [device.site, None]:
                raise serializers.ValidationError({
                    'tagged_vlans': f"VLAN {vlan} must belong to the same site as the interface's parent device, or "
                                    f"it must be global."
                })

        return super().validate(data)
