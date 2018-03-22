from __future__ import unicode_literals

from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import detail_route
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from dcim import filters
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site, VirtualChassis,
)
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.models import Graph, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from utilities.api import IsAuthenticatedOrLoginNotRequired, FieldChoicesViewSet, ModelViewSet, ServiceUnavailable
from . import serializers
from .exceptions import MissingFilterException


#
# Field choices
#

class DCIMFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Device, ['face', 'status']),
        (ConsolePort, ['connection_status']),
        (Interface, ['form_factor']),
        (InterfaceConnection, ['connection_status']),
        (InterfaceTemplate, ['form_factor']),
        (PowerPort, ['connection_status']),
        (Rack, ['type', 'width']),
    )


#
# Regions
#

class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = serializers.RegionSerializer
    write_serializer_class = serializers.WritableRegionSerializer
    filter_class = filters.RegionFilter


#
# Sites
#

class SiteViewSet(CustomFieldModelViewSet):
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

class RackGroupViewSet(ModelViewSet):
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
    filter_class = filters.RackRoleFilter


#
# Racks
#

class RackViewSet(CustomFieldModelViewSet):
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

class RackReservationViewSet(ModelViewSet):
    queryset = RackReservation.objects.select_related('rack', 'user', 'tenant')
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
    filter_class = filters.ManufacturerFilter


#
# Device types
#

class DeviceTypeViewSet(CustomFieldModelViewSet):
    queryset = DeviceType.objects.select_related('manufacturer')
    serializer_class = serializers.DeviceTypeSerializer
    write_serializer_class = serializers.WritableDeviceTypeSerializer
    filter_class = filters.DeviceTypeFilter


#
# Device type components
#

class ConsolePortTemplateViewSet(ModelViewSet):
    queryset = ConsolePortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsolePortTemplateSerializer
    write_serializer_class = serializers.WritableConsolePortTemplateSerializer
    filter_class = filters.ConsolePortTemplateFilter


class ConsoleServerPortTemplateViewSet(ModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    write_serializer_class = serializers.WritableConsoleServerPortTemplateSerializer
    filter_class = filters.ConsoleServerPortTemplateFilter


class PowerPortTemplateViewSet(ModelViewSet):
    queryset = PowerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerPortTemplateSerializer
    write_serializer_class = serializers.WritablePowerPortTemplateSerializer
    filter_class = filters.PowerPortTemplateFilter


class PowerOutletTemplateViewSet(ModelViewSet):
    queryset = PowerOutletTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerOutletTemplateSerializer
    write_serializer_class = serializers.WritablePowerOutletTemplateSerializer
    filter_class = filters.PowerOutletTemplateFilter


class InterfaceTemplateViewSet(ModelViewSet):
    queryset = InterfaceTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.InterfaceTemplateSerializer
    write_serializer_class = serializers.WritableInterfaceTemplateSerializer
    filter_class = filters.InterfaceTemplateFilter


class DeviceBayTemplateViewSet(ModelViewSet):
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
    filter_class = filters.DeviceRoleFilter


#
# Platforms
#

class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = serializers.PlatformSerializer
    write_serializer_class = serializers.WritablePlatformSerializer
    filter_class = filters.PlatformFilter


#
# Devices
#

class DeviceViewSet(CustomFieldModelViewSet):
    queryset = Device.objects.select_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'site', 'rack', 'parent_bay',
        'virtual_chassis__master',
    ).prefetch_related(
        'primary_ip4__nat_outside', 'primary_ip6__nat_outside',
    )
    serializer_class = serializers.DeviceSerializer
    write_serializer_class = serializers.WritableDeviceSerializer
    filter_class = filters.DeviceFilter

    @detail_route(url_path='napalm')
    def napalm(self, request, pk):
        """
        Execute a NAPALM method on a Device
        """
        device = get_object_or_404(Device, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable("This device does not have a primary IP address configured.")
        if device.platform is None:
            raise ServiceUnavailable("No platform is configured for this device.")
        if not device.platform.napalm_driver:
            raise ServiceUnavailable("No NAPALM driver is configured for this device's platform ().".format(
                device.platform
            ))

        # Check that NAPALM is installed
        try:
            import napalm
        except ImportError:
            raise ServiceUnavailable("NAPALM is not installed. Please see the documentation for instructions.")
        from napalm.base.exceptions import ConnectAuthError, ModuleImportError

        # Validate the configured driver
        try:
            driver = napalm.get_network_driver(device.platform.napalm_driver)
        except ModuleImportError:
            raise ServiceUnavailable("NAPALM driver for platform {} not found: {}.".format(
                device.platform, device.platform.napalm_driver
            ))

        # Verify user permission
        if not request.user.has_perm('dcim.napalm_read'):
            return HttpResponseForbidden()

        # Validate requested NAPALM methods
        napalm_methods = request.GET.getlist('method')
        for method in napalm_methods:
            if not hasattr(driver, method):
                return HttpResponseBadRequest("Unknown NAPALM method: {}".format(method))
            elif not method.startswith('get_'):
                return HttpResponseBadRequest("Unsupported NAPALM method: {}".format(method))

        # Connect to the device and execute the requested methods
        # TODO: Improve error handling
        response = OrderedDict([(m, None) for m in napalm_methods])
        ip_address = str(device.primary_ip.address.ip)
        d = driver(
            hostname=ip_address,
            username=settings.NAPALM_USERNAME,
            password=settings.NAPALM_PASSWORD,
            timeout=settings.NAPALM_TIMEOUT,
            optional_args=settings.NAPALM_ARGS
        )
        try:
            d.open()
            for method in napalm_methods:
                response[method] = getattr(d, method)()
        except Exception as e:
            raise ServiceUnavailable("Error connecting to the device at {}: {}".format(ip_address, e))

        d.close()
        return Response(response)


#
# Device components
#

class ConsolePortViewSet(ModelViewSet):
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device')
    serializer_class = serializers.ConsolePortSerializer
    write_serializer_class = serializers.WritableConsolePortSerializer
    filter_class = filters.ConsolePortFilter


class ConsoleServerPortViewSet(ModelViewSet):
    queryset = ConsoleServerPort.objects.select_related('device', 'connected_console__device')
    serializer_class = serializers.ConsoleServerPortSerializer
    write_serializer_class = serializers.WritableConsoleServerPortSerializer
    filter_class = filters.ConsoleServerPortFilter


class PowerPortViewSet(ModelViewSet):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device')
    serializer_class = serializers.PowerPortSerializer
    write_serializer_class = serializers.WritablePowerPortSerializer
    filter_class = filters.PowerPortFilter


class PowerOutletViewSet(ModelViewSet):
    queryset = PowerOutlet.objects.select_related('device', 'connected_port__device')
    serializer_class = serializers.PowerOutletSerializer
    write_serializer_class = serializers.WritablePowerOutletSerializer
    filter_class = filters.PowerOutletFilter


class InterfaceViewSet(ModelViewSet):
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


class DeviceBayViewSet(ModelViewSet):
    queryset = DeviceBay.objects.select_related('installed_device')
    serializer_class = serializers.DeviceBaySerializer
    write_serializer_class = serializers.WritableDeviceBaySerializer
    filter_class = filters.DeviceBayFilter


class InventoryItemViewSet(ModelViewSet):
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


class InterfaceConnectionViewSet(ModelViewSet):
    queryset = InterfaceConnection.objects.select_related('interface_a__device', 'interface_b__device')
    serializer_class = serializers.InterfaceConnectionSerializer
    write_serializer_class = serializers.WritableInterfaceConnectionSerializer
    filter_class = filters.InterfaceConnectionFilter


#
# Virtual chassis
#

class VirtualChassisViewSet(ModelViewSet):
    queryset = VirtualChassis.objects.all()
    serializer_class = serializers.VirtualChassisSerializer
    write_serializer_class = serializers.WritableVirtualChassisSerializer


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
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    _device_param = Parameter('peer-device', 'query',
                              description='The name of the peer device', required=True, type=openapi.TYPE_STRING)
    _interface_param = Parameter('peer-interface', 'query',
                                 description='The name of the peer interface', required=True, type=openapi.TYPE_STRING)

    def get_view_name(self):
        return "Connected Device Locator"

    @swagger_auto_schema(
        manual_parameters=[_device_param, _interface_param], responses={'200': serializers.DeviceSerializer})
    def list(self, request):

        peer_device_name = request.query_params.get(self._device_param.name)
        peer_interface_name = request.query_params.get(self._interface_param.name)
        if not peer_device_name or not peer_interface_name:
            raise MissingFilterException(detail='Request must include "peer-device" and "peer-interface" filters.')

        # Determine local interface from peer interface's connection
        peer_interface = get_object_or_404(Interface, device__name=peer_device_name, name=peer_interface_name)
        local_interface = peer_interface.connected_interface

        if local_interface is None:
            return Response()

        return Response(serializers.DeviceSerializer(local_interface.device, context={'request': request}).data)
