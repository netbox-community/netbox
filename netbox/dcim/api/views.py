from __future__ import unicode_literals

from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
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
        (Interface, ['form_factor', 'mode']),
        (InterfaceConnection, ['connection_status']),
        (InterfaceTemplate, ['form_factor']),
        (PowerPort, ['connection_status']),
        (Rack, ['type', 'width']),
        (Site, ['status']),
    )


#
# Regions
#

class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = serializers.RegionSerializer
    filter_class = filters.RegionFilter


#
# Sites
#

class SiteViewSet(CustomFieldModelViewSet):
    queryset = Site.objects.select_related('region', 'tenant').prefetch_related('tags')
    serializer_class = serializers.SiteSerializer
    filter_class = filters.SiteFilter

    @action(detail=True)
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
    queryset = Rack.objects.select_related('site', 'group__site', 'tenant').prefetch_related('tags')
    serializer_class = serializers.RackSerializer
    filter_class = filters.RackFilter

    @action(detail=True)
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
    queryset = DeviceType.objects.select_related('manufacturer').prefetch_related('tags')
    serializer_class = serializers.DeviceTypeSerializer
    filter_class = filters.DeviceTypeFilter


#
# Device type components
#

class ConsolePortTemplateViewSet(ModelViewSet):
    queryset = ConsolePortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsolePortTemplateSerializer
    filter_class = filters.ConsolePortTemplateFilter


class ConsoleServerPortTemplateViewSet(ModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    filter_class = filters.ConsoleServerPortTemplateFilter


class PowerPortTemplateViewSet(ModelViewSet):
    queryset = PowerPortTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerPortTemplateSerializer
    filter_class = filters.PowerPortTemplateFilter


class PowerOutletTemplateViewSet(ModelViewSet):
    queryset = PowerOutletTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.PowerOutletTemplateSerializer
    filter_class = filters.PowerOutletTemplateFilter


class InterfaceTemplateViewSet(ModelViewSet):
    queryset = InterfaceTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.InterfaceTemplateSerializer
    filter_class = filters.InterfaceTemplateFilter


class DeviceBayTemplateViewSet(ModelViewSet):
    queryset = DeviceBayTemplate.objects.select_related('device_type__manufacturer')
    serializer_class = serializers.DeviceBayTemplateSerializer
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
    filter_class = filters.PlatformFilter


#
# Devices
#

class DeviceViewSet(CustomFieldModelViewSet):
    queryset = Device.objects.select_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'site', 'rack', 'parent_bay',
        'virtual_chassis__master',
    ).prefetch_related(
        'primary_ip4__nat_outside', 'primary_ip6__nat_outside', 'tags',
    )
    filter_class = filters.DeviceFilter

    def get_serializer_class(self):
        """
        Include rendered config context when retrieving a single Device.
        """
        if self.action == 'retrieve':
            return serializers.DeviceWithConfigContextSerializer

        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            return serializers.NestedDeviceSerializer

        return serializers.DeviceSerializer

    @action(detail=True, url_path='napalm')
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
            from napalm.base.exceptions import ModuleImportError
        except ImportError:
            raise ServiceUnavailable("NAPALM is not installed. Please see the documentation for instructions.")

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

        # Connect to the device
        napalm_methods = request.GET.getlist('method')
        response = OrderedDict([(m, None) for m in napalm_methods])
        ip_address = str(device.primary_ip.address.ip)
        optional_args = settings.NAPALM_ARGS.copy()
        if device.platform.napalm_args is not None:
            optional_args.update(device.platform.napalm_args)
        d = driver(
            hostname=ip_address,
            username=settings.NAPALM_USERNAME,
            password=settings.NAPALM_PASSWORD,
            timeout=settings.NAPALM_TIMEOUT,
            optional_args=optional_args
        )
        try:
            d.open()
        except Exception as e:
            raise ServiceUnavailable("Error connecting to the device at {}: {}".format(ip_address, e))

        # Validate and execute each specified NAPALM method
        for method in napalm_methods:
            if not hasattr(driver, method):
                response[method] = {'error': 'Unknown NAPALM method'}
                continue
            if not method.startswith('get_'):
                response[method] = {'error': 'Only get_* NAPALM methods are supported'}
                continue
            try:
                response[method] = getattr(d, method)()
            except NotImplementedError:
                response[method] = {'error': 'Method {} not implemented for NAPALM driver {}'.format(method, driver)}
            except Exception as e:
                response[method] = {'error': 'Method {} failed: {}'.format(method, e)}
        d.close()

        return Response(response)


#
# Device components
#

class ConsolePortViewSet(ModelViewSet):
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device').prefetch_related('tags')
    serializer_class = serializers.ConsolePortSerializer
    filter_class = filters.ConsolePortFilter


class ConsoleServerPortViewSet(ModelViewSet):
    queryset = ConsoleServerPort.objects.select_related('device', 'connected_console__device').prefetch_related('tags')
    serializer_class = serializers.ConsoleServerPortSerializer
    filter_class = filters.ConsoleServerPortFilter


class PowerPortViewSet(ModelViewSet):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device').prefetch_related('tags')
    serializer_class = serializers.PowerPortSerializer
    filter_class = filters.PowerPortFilter


class PowerOutletViewSet(ModelViewSet):
    queryset = PowerOutlet.objects.select_related('device', 'connected_port__device').prefetch_related('tags')
    serializer_class = serializers.PowerOutletSerializer
    filter_class = filters.PowerOutletFilter


class InterfaceViewSet(ModelViewSet):
    queryset = Interface.objects.select_related('device').prefetch_related('tags')
    serializer_class = serializers.InterfaceSerializer
    filter_class = filters.InterfaceFilter

    @action(detail=True)
    def graphs(self, request, pk=None):
        """
        A convenience method for rendering graphs for a particular interface.
        """
        interface = get_object_or_404(Interface, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': interface})
        return Response(serializer.data)


class DeviceBayViewSet(ModelViewSet):
    queryset = DeviceBay.objects.select_related('installed_device').prefetch_related('tags')
    serializer_class = serializers.DeviceBaySerializer
    filter_class = filters.DeviceBayFilter


class InventoryItemViewSet(ModelViewSet):
    queryset = InventoryItem.objects.select_related('device', 'manufacturer').prefetch_related('tags')
    serializer_class = serializers.InventoryItemSerializer
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
    filter_class = filters.InterfaceConnectionFilter


#
# Virtual chassis
#

class VirtualChassisViewSet(ModelViewSet):
    queryset = VirtualChassis.objects.prefetch_related('tags')
    serializer_class = serializers.VirtualChassisSerializer


#
# Miscellaneous
#

class ConnectedDeviceViewSet(ViewSet):
    """
    This endpoint allows a user to determine what device (if any) is connected to a given peer device and peer
    interface. This is useful in a situation where a device boots with no configuration, but can detect its neighbors
    via a protocol such as LLDP. Two query parameters must be included in the request:

    * `peer_device`: The name of the peer device
    * `peer_interface`: The name of the peer interface
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    _device_param = Parameter('peer_device', 'query',
                              description='The name of the peer device', required=True, type=openapi.TYPE_STRING)
    _interface_param = Parameter('peer_interface', 'query',
                                 description='The name of the peer interface', required=True, type=openapi.TYPE_STRING)

    def get_view_name(self):
        return "Connected Device Locator"

    @swagger_auto_schema(
        manual_parameters=[_device_param, _interface_param], responses={'200': serializers.DeviceSerializer})
    def list(self, request):

        peer_device_name = request.query_params.get(self._device_param.name)
        if not peer_device_name:
            # TODO: remove this after 2.4 as the switch to using underscores is a breaking change
            peer_device_name = request.query_params.get('peer-device')
        peer_interface_name = request.query_params.get(self._interface_param.name)
        if not peer_interface_name:
            # TODO: remove this after 2.4 as the switch to using underscores is a breaking change
            peer_interface_name = request.query_params.get('peer-interface')
        if not peer_device_name or not peer_interface_name:
            raise MissingFilterException(detail='Request must include "peer_device" and "peer_interface" filters.')

        # Determine local interface from peer interface's connection
        peer_interface = get_object_or_404(Interface, device__name=peer_device_name, name=peer_interface_name)
        local_interface = peer_interface.connected_interface

        if local_interface is None:
            return Response()

        return Response(serializers.DeviceSerializer(local_interface.device, context={'request': request}).data)
