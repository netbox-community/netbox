from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from dcim.models import (
    ConsolePort, ConsoleServerPort, Device, DeviceBay, DeviceRole, DeviceType, Interface, InterfaceConnection,
    Manufacturer, Module, Platform, PowerOutlet, PowerPort, Rack, RackGroup, RackRole, Site,
)
from dcim import filters
from extras.api.views import CustomFieldModelViewSet
from extras.api.renderers import BINDZoneRenderer, FlatJSONRenderer
from utilities.api import ServiceUnavailable, WritableSerializerMixin
from .exceptions import MissingFilterException
from . import serializers


#
# Sites
#

class SiteViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Site.objects.select_related('tenant')
    serializer_class = serializers.SiteSerializer


#
# Rack groups
#

class RackGroupViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = RackGroup.objects.select_related('site')
    serializer_class = serializers.RackGroupSerializer
    filter_class = filters.RackGroupFilter


#
# Rack roles
#

class RackRoleViewSet(ModelViewSet):
    queryset = RackRole.objects.all()
    serializer_class = serializers.RackRoleSerializer


#
# Racks
#

class RackViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Rack.objects.select_related('site', 'group__site', 'tenant')
    serializer_class = serializers.RackSerializer
    filter_class = filters.RackFilter


class RackUnitListView(APIView):
    """
    List rack units (by rack)
    """

    def get(self, request, pk):

        rack = get_object_or_404(Rack, pk=pk)
        face = request.GET.get('face', 0)
        exclude_pk = request.GET.get('exclude', None)
        if exclude_pk is not None:
            try:
                exclude_pk = int(exclude_pk)
            except ValueError:
                exclude_pk = None
        elevation = rack.get_rack_units(face, exclude_pk)

        # Serialize Devices within the rack elevation
        for u in elevation:
            if u['device']:
                u['device'] = serializers.NestedDeviceSerializer(
                    instance=u['device'],
                    context={'request': request},
                ).data

        return Response(elevation)


#
# Manufacturers
#

class ManufacturerViewSet(ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer


#
# Device Types
#

class DeviceTypeViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = DeviceType.objects.select_related('manufacturer')
    serializer_class = serializers.DeviceTypeSerializer


#
# Device Roles
#

class DeviceRoleViewSet(ModelViewSet):
    queryset = DeviceRole.objects.all()
    serializer_class = serializers.DeviceRoleSerializer


#
# Platforms
#

class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = serializers.PlatformSerializer


#
# Devices
#

class DeviceViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Device.objects.select_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'rack__site', 'parent_bay',
    ).prefetch_related(
        'primary_ip4__nat_outside', 'primary_ip6__nat_outside',
    )
    serializer_class = serializers.DeviceSerializer
    filter_class = filters.DeviceFilter
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [BINDZoneRenderer, FlatJSONRenderer]


#
# Console Ports
#

class ConsolePortViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                         GenericViewSet):
    queryset = ConsolePort.objects.select_related('cs_port')
    serializer_class = serializers.ConsolePortSerializer


class ChildConsolePortViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildConsoleServerPortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return ConsolePort.objects.filter(device=device).select_related('cs_port')


#
# Console Server Ports
#

class ConsoleServerPortViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                               GenericViewSet):
    queryset = ConsoleServerPort.objects.select_related('connected_console')
    serializer_class = serializers.ConsoleServerPortSerializer


class ChildConsoleServerPortViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildConsoleServerPortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return ConsoleServerPort.objects.filter(device=device).select_related('connected_console')


#
# Power Ports
#

class PowerPortViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                       GenericViewSet):
    queryset = PowerPort.objects.select_related('power_outlet')
    serializer_class = serializers.PowerPortSerializer


class NestedPowerPortViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildPowerPortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return PowerPort.objects.filter(device=device).select_related('power_outlet')


#
# Power Outlets
#

class PowerOutletViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                         GenericViewSet):
    queryset = PowerOutlet.objects.select_related('connected_port')
    serializer_class = serializers.PowerOutletSerializer


class NestedPowerOutletViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildPowerOutletSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return PowerOutlet.objects.filter(device=device).select_related('connected_port')


#
# Interfaces
#

class InterfaceViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                       GenericViewSet):
    queryset = Interface.objects.select_related('device')
    serializer_class = serializers.InterfaceDetailSerializer


class NestedInterfaceViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildInterfaceSerializer
    filter_class = filters.InterfaceFilter

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return Interface.objects.order_naturally(device.device_type.interface_ordering).filter(device=device)\
            .select_related('connected_as_a', 'connected_as_b', 'circuit_termination')


#
# Device bays
#

class DeviceBayViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin,
                       GenericViewSet):
    queryset = DeviceBay.objects.select_related('installed_device')
    serializer_class = serializers.DeviceBaySerializer


class NestedDeviceBayViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildDeviceBaySerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return DeviceBay.objects.filter(device=device).select_related('installed_device')


#
# Modules
#

class ModuleViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin, GenericViewSet):
    queryset = Module.objects.select_related('device', 'manufacturer')
    serializer_class = serializers.ModuleSerializer


class NestedModuleViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.ChildModuleSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return Module.objects.filter(device=device).select_related('device', 'manufacturer')


#
# Interface connections
#

class InterfaceConnectionViewSet(ModelViewSet):
    queryset = InterfaceConnection.objects.all()
    serializer_class = serializers.InterfaceConnectionSerializer


#
# Live queries
#

class LLDPNeighborsView(APIView):
    """
    Retrieve live LLDP neighbors of a device
    """

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable(detail="No IP configured for this device.")

        RPC = device.get_rpc_client()
        if not RPC:
            raise ServiceUnavailable(detail="No RPC client available for this platform ({}).".format(device.platform))

        # Connect to device and retrieve inventory info
        try:
            with RPC(device, username=settings.NETBOX_USERNAME, password=settings.NETBOX_PASSWORD) as rpc_client:
                lldp_neighbors = rpc_client.get_lldp_neighbors()
        except:
            raise ServiceUnavailable(detail="Error connecting to the remote device.")

        return Response(lldp_neighbors)


#
# Miscellaneous
#

class RelatedConnectionsView(APIView):
    """
    Retrieve all connections related to a given console/power/interface connection
    """

    def __init__(self):
        super(RelatedConnectionsView, self).__init__()

        # Custom fields
        content_type = ContentType.objects.get_for_model(Device)
        custom_fields = content_type.custom_fields.prefetch_related('choices')

        # Cache all relevant CustomFieldChoices. This saves us from having to do a lookup per select field per object.
        custom_field_choices = {}
        for field in custom_fields:
            for cfc in field.choices.all():
                custom_field_choices[cfc.id] = cfc.value

        self.context = {
            'custom_fields': custom_fields,
            'custom_field_choices': custom_field_choices,
        }

    def get(self, request):

        peer_device = request.GET.get('peer-device')
        peer_interface = request.GET.get('peer-interface')

        # Search by interface
        if peer_device and peer_interface:

            # Determine local interface from peer interface's connection
            try:
                peer_iface = Interface.objects.get(device__name=peer_device, name=peer_interface)
            except Interface.DoesNotExist:
                raise Http404()
            local_iface = peer_iface.connected_interface
            if local_iface:
                device = local_iface.device
            else:
                return Response()

        else:
            raise MissingFilterException(detail='Must specify search parameters "peer-device" and "peer-interface".')

        # Initialize response skeleton
        response = {
            'device': serializers.DeviceSerializer(device, context=self.context).data,
            'console-ports': [],
            'power-ports': [],
            'interfaces': [],
        }

        # Console connections
        console_ports = ConsolePort.objects.filter(device=device).select_related('cs_port__device')
        for cp in console_ports:
            data = serializers.ConsolePortSerializer(instance=cp).data
            del(data['device'])
            response['console-ports'].append(data)

        # Power connections
        power_ports = PowerPort.objects.filter(device=device).select_related('power_outlet__device')
        for pp in power_ports:
            data = serializers.PowerPortSerializer(instance=pp).data
            del(data['device'])
            response['power-ports'].append(data)

        # Interface connections
        interfaces = Interface.objects.order_naturally(device.device_type.interface_ordering).filter(device=device)\
            .select_related('connected_as_a', 'connected_as_b', 'circuit_termination')
        for iface in interfaces:
            data = serializers.InterfaceDetailSerializer(instance=iface).data
            del(data['device'])
            response['interfaces'].append(data)

        return Response(response)
