from __future__ import unicode_literals

from rest_framework.decorators import detail_route
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

from django.conf import settings
from django.shortcuts import get_object_or_404

from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site,
)
from dcim import filters
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from utilities.api import ServiceUnavailable, WritableSerializerMixin
from .exceptions import MissingFilterException
from . import serializers


#
# Regions
#

class RegionViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = serializers.RegionSerializer
    write_serializer_class = serializers.WritableRegionSerializer


#
# Sites
#

class SiteViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Site.objects.select_related('region', 'tenant')
    serializer_class = serializers.SiteSerializer
    write_serializer_class = serializers.WritableSiteSerializer
    filter_class = filters.SiteFilter

    @detail_route()
    def graphs(self, request, pk=None):
        """
        A convenience method for rendering graphs for a particular site.
        """
        site = get_object_or_404(Site, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_SITE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': site})
        return Response(serializer.data)


#
# Rack groups
#

class RackGroupViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = RackGroup.objects.select_related('site')
    serializer_class = serializers.RackGroupSerializer
    write_serializer_class = serializers.WritableRackGroupSerializer
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
    write_serializer_class = serializers.WritableRackSerializer
    filter_class = filters.RackFilter

    @detail_route()
    def units(self, request, pk=None):
        """
        List rack units (by rack)
        """
        rack = get_object_or_404(Rack, pk=pk)
        face = request.GET.get('face', 0)
        exclude_pk = request.GET.get('exclude', None)
        if exclude_pk is not None:
            try:
                exclude_pk = int(exclude_pk)
            except ValueError:
                exclude_pk = None
        elevation = rack.get_rack_units(face, exclude_pk)

        page = self.paginate_queryset(elevation)
        if page is not None:
            rack_units = serializers.RackUnitSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(rack_units.data)


#
# Rack reservations
#

class RackReservationViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = RackReservation.objects.select_related('rack')
    serializer_class = serializers.RackReservationSerializer
    write_serializer_class = serializers.WritableRackReservationSerializer
    filter_class = filters.RackReservationFilter

    # Assign user from request
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


#
# Manufacturers
#

class ManufacturerViewSet(ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer


#
# Device types
#

class DeviceTypeViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = DeviceType.objects.select_related('manufacturer')
    serializer_class = serializers.DeviceTypeSerializer
    write_serializer_class = serializers.WritableDeviceTypeSerializer
    filter_class = filters.DeviceTypeFilter


#
# Device type components
#

class ConsolePortTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = ConsolePortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsolePortTemplateSerializer
    write_serializer_class = serializers.WritableConsolePortTemplateSerializer
    filter_class = filters.ConsolePortTemplateFilter


class ConsoleServerPortTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    write_serializer_class = serializers.WritableConsoleServerPortTemplateSerializer
    filter_class = filters.ConsoleServerPortTemplateFilter


class PowerPortTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = PowerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerPortTemplateSerializer
    write_serializer_class = serializers.WritablePowerPortTemplateSerializer
    filter_class = filters.PowerPortTemplateFilter


class PowerOutletTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = PowerOutletTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerOutletTemplateSerializer
    write_serializer_class = serializers.WritablePowerOutletTemplateSerializer
    filter_class = filters.PowerOutletTemplateFilter


class InterfaceTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = InterfaceTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.InterfaceTemplateSerializer
    write_serializer_class = serializers.WritableInterfaceTemplateSerializer
    filter_class = filters.InterfaceTemplateFilter


class DeviceBayTemplateViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = DeviceBayTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.DeviceBayTemplateSerializer
    write_serializer_class = serializers.WritableDeviceBayTemplateSerializer
    filter_class = filters.DeviceBayTemplateFilter


#
# Device roles
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
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'site', 'rack', 'parent_bay',
    ).prefetch_related(
        'primary_ip4__nat_outside', 'primary_ip6__nat_outside',
    )
    serializer_class = serializers.DeviceSerializer
    write_serializer_class = serializers.WritableDeviceSerializer
    filter_class = filters.DeviceFilter

    @detail_route(url_path='lldp-neighbors')
    def lldp_neighbors(self, request, pk):
        """
        Retrieve live LLDP neighbors of a device
        """
        device = get_object_or_404(Device, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable("No IP configured for this device.")

        RPC = device.get_rpc_client()
        if not RPC:
            raise ServiceUnavailable("No RPC client available for this platform ({}).".format(device.platform))

        # Connect to device and retrieve inventory info
        try:
            with RPC(device, username=settings.NETBOX_USERNAME, password=settings.NETBOX_PASSWORD) as rpc_client:
                lldp_neighbors = rpc_client.get_lldp_neighbors()
        except:
            raise ServiceUnavailable("Error connecting to the remote device.")

        return Response(lldp_neighbors)


#
# Device components
#

class ConsolePortViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device')
    serializer_class = serializers.ConsolePortSerializer
    write_serializer_class = serializers.WritableConsolePortSerializer
    filter_class = filters.ConsolePortFilter


class ConsoleServerPortViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = ConsoleServerPort.objects.select_related('device', 'connected_console__device')
    serializer_class = serializers.ConsoleServerPortSerializer
    write_serializer_class = serializers.WritableConsoleServerPortSerializer
    filter_class = filters.ConsoleServerPortFilter


class PowerPortViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device')
    serializer_class = serializers.PowerPortSerializer
    write_serializer_class = serializers.WritablePowerPortSerializer
    filter_class = filters.PowerPortFilter


class PowerOutletViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = PowerOutlet.objects.select_related('device', 'connected_port__device')
    serializer_class = serializers.PowerOutletSerializer
    write_serializer_class = serializers.WritablePowerOutletSerializer
    filter_class = filters.PowerOutletFilter


class InterfaceViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Interface.objects.select_related('device')
    serializer_class = serializers.InterfaceSerializer
    write_serializer_class = serializers.WritableInterfaceSerializer
    filter_class = filters.InterfaceFilter

    @detail_route()
    def graphs(self, request, pk=None):
        """
        A convenience method for rendering graphs for a particular interface.
        """
        interface = get_object_or_404(Interface, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': interface})
        return Response(serializer.data)


class DeviceBayViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = DeviceBay.objects.select_related('installed_device')
    serializer_class = serializers.DeviceBaySerializer
    write_serializer_class = serializers.WritableDeviceBaySerializer
    filter_class = filters.DeviceBayFilter


class InventoryItemViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = InventoryItem.objects.select_related('device', 'manufacturer')
    serializer_class = serializers.InventoryItemSerializer
    write_serializer_class = serializers.WritableInventoryItemSerializer
    filter_class = filters.InventoryItemFilter


#
# Connections
#

class ConsoleConnectionViewSet(ListModelMixin, GenericViewSet):
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device').filter(cs_port__isnull=False)
    serializer_class = serializers.ConsolePortSerializer
    filter_class = filters.ConsoleConnectionFilter


class PowerConnectionViewSet(ListModelMixin, GenericViewSet):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device').filter(power_outlet__isnull=False)
    serializer_class = serializers.PowerPortSerializer
    filter_class = filters.PowerConnectionFilter


class InterfaceConnectionViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = InterfaceConnection.objects.select_related('interface_a__device', 'interface_b__device')
    serializer_class = serializers.InterfaceConnectionSerializer
    write_serializer_class = serializers.WritableInterfaceConnectionSerializer
    filter_class = filters.InterfaceConnectionFilter


#
# Miscellaneous
#

class ConnectedDeviceViewSet(ViewSet):
    """
    This endpoint allows a user to determine what device (if any) is connected to a given peer device and peer
    interface. This is useful in a situation where a device boots with no configuration, but can detect its neighbors
    via a protocol such as LLDP. Two query parameters must be included in the request:

    * `peer-device`: The name of the peer device
    * `peer-interface`: The name of the peer interface
    """
    permission_classes = [IsAuthenticated]

    def get_view_name(self):
        return "Connected Device Locator"

    def list(self, request):

        peer_device_name = request.query_params.get('peer-device')
        peer_interface_name = request.query_params.get('peer-interface')
        if not peer_device_name or not peer_interface_name:
            raise MissingFilterException(detail='Request must include "peer-device" and "peer-interface" filters.')

        # Determine local interface from peer interface's connection
        peer_interface = get_object_or_404(Interface, device__name=peer_device_name, name=peer_interface_name)
        local_interface = peer_interface.connected_interface

        if local_interface is None:
            return Response()

        return Response(serializers.DeviceSerializer(local_interface.device, context={'request': request}).data)
