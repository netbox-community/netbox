from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from dcim.models import (
    ConsolePort, ConsoleServerPort, Device, DeviceBay, DeviceRole, DeviceType, IFACE_FF_VIRTUAL, Interface,
    InterfaceConnection, Manufacturer, Module, Platform, PowerOutlet, PowerPort, Rack, RackGroup, RackRole, Site,
)
from dcim import filters
from extras.api.views import CustomFieldModelViewSet
from extras.api.renderers import BINDZoneRenderer, FlatJSONRenderer
from utilities.api import ServiceUnavailable
from .exceptions import MissingFilterException
from . import serializers


#
# Sites
#

class SiteViewSet(CustomFieldModelViewSet):
    """
    List and retrieve sites
    """
    queryset = Site.objects.select_related('tenant')
    serializer_class = serializers.SiteSerializer


#
# Rack groups
#

class RackGroupViewSet(ModelViewSet):
    """
    List and retrieve rack groups
    """
    queryset = RackGroup.objects.select_related('site')
    serializer_class = serializers.RackGroupSerializer
    filter_class = filters.RackGroupFilter


#
# Rack roles
#

class RackRoleViewSet(ModelViewSet):
    """
    List and retrieve rack roles
    """
    queryset = RackRole.objects.all()
    serializer_class = serializers.RackRoleSerializer


#
# Racks
#

class RackViewSet(CustomFieldModelViewSet):
    """
    List and retrieve racks
    """
    queryset = Rack.objects.select_related('site', 'group__site', 'tenant')
    filter_class = filters.RackFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.RackDetailSerializer
        return serializers.RackSerializer


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
                u['device'] = serializers.DeviceNestedSerializer(instance=u['device']).data

        return Response(elevation)


#
# Manufacturers
#

class ManufacturerViewSet(ModelViewSet):
    """
    List and retrieve manufacturers
    """
    queryset = Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer


#
# Device Types
#

class DeviceTypeViewSet(CustomFieldModelViewSet):
    """
    List and retrieve device types
    """
    queryset = DeviceType.objects.select_related('manufacturer')
    filter_class = filters.DeviceTypeFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.DeviceTypeDetailSerializer
        return serializers.DeviceTypeSerializer


#
# Device roles
#

class DeviceRoleViewSet(ModelViewSet):
    """
    List and retrieve device roles
    """
    queryset = DeviceRole.objects.all()
    serializer_class = serializers.DeviceRoleSerializer


#
# Platforms
#

class PlatformViewSet(ModelViewSet):
    """
    List and retrieve platforms
    """
    queryset = Platform.objects.all()
    serializer_class = serializers.PlatformSerializer


#
# Devices
#

class DeviceViewSet(CustomFieldModelViewSet):
    """
    List and retrieve devices
    """
    queryset = Device.objects.select_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'rack__site', 'parent_bay',
    ).prefetch_related(
        'primary_ip4__nat_outside', 'primary_ip6__nat_outside',
    )
    serializer_class = serializers.DeviceSerializer
    filter_class = filters.DeviceFilter
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [BINDZoneRenderer, FlatJSONRenderer]


#
# Console ports
#

class ConsolePortViewSet(ModelViewSet):
    """
    List and retrieve console ports (by device)
    """
    serializer_class = serializers.ConsolePortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return ConsolePort.objects.filter(device=device).select_related('cs_port')


class ConsolePortView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = serializers.ConsolePortSerializer
    queryset = ConsolePort.objects.all()


#
# Console server ports
#

class ConsoleServerPortViewSet(ModelViewSet):
    """
    List and retrieve console server ports (by device)
    """
    serializer_class = serializers.ConsoleServerPortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return ConsoleServerPort.objects.filter(device=device).select_related('connected_console')


#
# Power ports
#

class PowerPortViewSet(ModelViewSet):
    """
    List and retrieve power ports (by device)
    """
    serializer_class = serializers.PowerPortSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return PowerPort.objects.filter(device=device).select_related('power_outlet')


class PowerPortView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = serializers.PowerPortSerializer
    queryset = PowerPort.objects.all()


#
# Power outlets
#

class PowerOutletViewSet(ModelViewSet):
    """
    List and retrieve power outlets (by device)
    """
    serializer_class = serializers.PowerOutletSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return PowerOutlet.objects.filter(device=device).select_related('connected_port')


#
# Interfaces
#

class InterfaceViewSet(ModelViewSet):
    """
    List and retrieve interfaces (by device)
    """
    serializer_class = serializers.InterfaceSerializer
    filter_class = filters.InterfaceFilter

    def get_queryset(self):

        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        queryset = Interface.objects.order_naturally(device.device_type.interface_ordering).filter(device=device)\
            .select_related('connected_as_a', 'connected_as_b', 'circuit_termination')

        # Filter by type (physical or virtual)
        iface_type = self.request.query_params.get('type')
        if iface_type == 'physical':
            queryset = queryset.exclude(form_factor=IFACE_FF_VIRTUAL)
        elif iface_type == 'virtual':
            queryset = queryset.filter(form_factor=IFACE_FF_VIRTUAL)
        elif iface_type is not None:
            queryset = queryset.empty()

        return queryset


class InterfaceDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single interface
    """
    queryset = Interface.objects.select_related('device')
    serializer_class = serializers.InterfaceDetailSerializer


class InterfaceConnectionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = serializers.InterfaceConnectionSerializer
    queryset = InterfaceConnection.objects.all()


class InterfaceConnectionListView(generics.ListAPIView):
    """
    Retrieve a list of all interface connections
    """
    serializer_class = serializers.InterfaceConnectionSerializer
    queryset = InterfaceConnection.objects.all()


#
# Device bays
#

class DeviceBayViewSet(ModelViewSet):
    """
    List and retrieve device bays (by device)
    """
    serializer_class = serializers.DeviceBayNestedSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return DeviceBay.objects.filter(device=device).select_related('installed_device')


#
# Modules
#

class ModuleViewSet(ModelViewSet):
    """
    List and retrieve modules (by device)
    """
    serializer_class = serializers.ModuleSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return Module.objects.filter(device=device).select_related('device', 'manufacturer')


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
