from collections import OrderedDict

from django.conf import settings
from django.db.models import Count, F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from circuits.models import Circuit
from dcim import filters
from dcim.models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    Manufacturer, InventoryItem, Platform, PowerFeed, PowerOutlet, PowerOutletTemplate, PowerPanel, PowerPort,
    PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site,
    VirtualChassis,
)
from extras.api.serializers import RenderedGraphSerializer
from extras.api.views import CustomFieldModelViewSet
from extras.constants import GRAPH_TYPE_DEVICE, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.models import Graph
from ipam.models import Prefix, VLAN
from utilities.api import (
    get_serializer_for_model, IsAuthenticatedOrLoginNotRequired, FieldChoicesViewSet, ModelViewSet, ServiceUnavailable,
)
from utilities.utils import get_subquery
from virtualization.models import VirtualMachine
from . import serializers
from .exceptions import MissingFilterException


#
# Field choices
#

class DCIMFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Cable, ['length_unit', 'status', 'termination_a_type', 'termination_b_type', 'type']),
        (ConsolePort, ['connection_status']),
        (Device, ['face', 'status']),
        (DeviceType, ['subdevice_role']),
        (FrontPort, ['type']),
        (FrontPortTemplate, ['type']),
        (Interface, ['type', 'mode']),
        (InterfaceTemplate, ['type']),
        (PowerOutlet, ['feed_leg']),
        (PowerOutletTemplate, ['feed_leg']),
        (PowerPort, ['connection_status']),
        (Rack, ['outer_unit', 'status', 'type', 'width']),
        (RearPort, ['type']),
        (RearPortTemplate, ['type']),
        (Site, ['status']),
    )


# Mixins

class CableTraceMixin(object):

    @action(detail=True, url_path='trace')
    def trace(self, request, pk):
        """
        Trace a complete cable path and return each segment as a three-tuple of (termination, cable, termination).
        """
        obj = get_object_or_404(self.queryset.model, pk=pk)

        # Initialize the path array
        path = []

        for near_end, cable, far_end in obj.trace(follow_circuits=True):

            # Serialize each object
            serializer_a = get_serializer_for_model(near_end, prefix='Nested')
            x = serializer_a(near_end, context={'request': request}).data
            if cable is not None:
                y = serializers.TracedCableSerializer(cable, context={'request': request}).data
            else:
                y = None
            if far_end is not None:
                serializer_b = get_serializer_for_model(far_end, prefix='Nested')
                z = serializer_b(far_end, context={'request': request}).data
            else:
                z = None

            path.append((x, y, z))

        return Response(path)


#
# Regions
#

class RegionViewSet(ModelViewSet):
    queryset = Region.objects.annotate(
        site_count=Count('sites')
    )
    serializer_class = serializers.RegionSerializer
    filterset_class = filters.RegionFilter


#
# Sites
#

class SiteViewSet(CustomFieldModelViewSet):
    queryset = Site.objects.prefetch_related(
        'region', 'tenant', 'tags'
    ).annotate(
        device_count=get_subquery(Device, 'site'),
        rack_count=get_subquery(Rack, 'site'),
        prefix_count=get_subquery(Prefix, 'site'),
        vlan_count=get_subquery(VLAN, 'site'),
        circuit_count=get_subquery(Circuit, 'terminations__site'),
        virtualmachine_count=get_subquery(VirtualMachine, 'cluster__site'),
    )
    serializer_class = serializers.SiteSerializer
    filterset_class = filters.SiteFilter

    @action(detail=True)
    def graphs(self, request, pk):
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
    queryset = RackGroup.objects.prefetch_related('site').annotate(
        rack_count=Count('racks')
    )
    serializer_class = serializers.RackGroupSerializer
    filterset_class = filters.RackGroupFilter


#
# Rack roles
#

class RackRoleViewSet(ModelViewSet):
    queryset = RackRole.objects.annotate(
        rack_count=Count('racks')
    )
    serializer_class = serializers.RackRoleSerializer
    filterset_class = filters.RackRoleFilter


#
# Racks
#

class RackViewSet(CustomFieldModelViewSet):
    queryset = Rack.objects.prefetch_related(
        'site', 'group__site', 'role', 'tenant', 'tags'
    ).annotate(
        device_count=get_subquery(Device, 'rack'),
        powerfeed_count=get_subquery(PowerFeed, 'rack')
    )
    serializer_class = serializers.RackSerializer
    filterset_class = filters.RackFilter

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

        # Enable filtering rack units by ID
        q = request.GET.get('q', None)
        if q:
            elevation = [u for u in elevation if q in str(u['id'])]

        page = self.paginate_queryset(elevation)
        if page is not None:
            rack_units = serializers.RackUnitSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(rack_units.data)


#
# Rack reservations
#

class RackReservationViewSet(ModelViewSet):
    queryset = RackReservation.objects.prefetch_related('rack', 'user', 'tenant')
    serializer_class = serializers.RackReservationSerializer
    filterset_class = filters.RackReservationFilter

    # Assign user from request
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


#
# Manufacturers
#

class ManufacturerViewSet(ModelViewSet):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=get_subquery(DeviceType, 'manufacturer'),
        inventoryitem_count=get_subquery(InventoryItem, 'manufacturer'),
        platform_count=get_subquery(Platform, 'manufacturer')
    )
    serializer_class = serializers.ManufacturerSerializer
    filterset_class = filters.ManufacturerFilter


#
# Device types
#

class DeviceTypeViewSet(CustomFieldModelViewSet):
    queryset = DeviceType.objects.prefetch_related('manufacturer').prefetch_related('tags').annotate(
        device_count=Count('instances')
    )
    serializer_class = serializers.DeviceTypeSerializer
    filterset_class = filters.DeviceTypeFilter


#
# Device type components
#

class ConsolePortTemplateViewSet(ModelViewSet):
    queryset = ConsolePortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.ConsolePortTemplateSerializer
    filterset_class = filters.ConsolePortTemplateFilter


class ConsoleServerPortTemplateViewSet(ModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    filterset_class = filters.ConsoleServerPortTemplateFilter


class PowerPortTemplateViewSet(ModelViewSet):
    queryset = PowerPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.PowerPortTemplateSerializer
    filterset_class = filters.PowerPortTemplateFilter


class PowerOutletTemplateViewSet(ModelViewSet):
    queryset = PowerOutletTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.PowerOutletTemplateSerializer
    filterset_class = filters.PowerOutletTemplateFilter


class InterfaceTemplateViewSet(ModelViewSet):
    queryset = InterfaceTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.InterfaceTemplateSerializer
    filterset_class = filters.InterfaceTemplateFilter


class FrontPortTemplateViewSet(ModelViewSet):
    queryset = FrontPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.FrontPortTemplateSerializer
    filterset_class = filters.FrontPortTemplateFilter


class RearPortTemplateViewSet(ModelViewSet):
    queryset = RearPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.RearPortTemplateSerializer
    filterset_class = filters.RearPortTemplateFilter


class DeviceBayTemplateViewSet(ModelViewSet):
    queryset = DeviceBayTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.DeviceBayTemplateSerializer
    filterset_class = filters.DeviceBayTemplateFilter


#
# Device roles
#

class DeviceRoleViewSet(ModelViewSet):
    queryset = DeviceRole.objects.annotate(
        device_count=get_subquery(Device, 'device_role'),
        virtualmachine_count=get_subquery(VirtualMachine, 'role')
    )
    serializer_class = serializers.DeviceRoleSerializer
    filterset_class = filters.DeviceRoleFilter


#
# Platforms
#

class PlatformViewSet(ModelViewSet):
    queryset = Platform.objects.annotate(
        device_count=get_subquery(Device, 'platform'),
        virtualmachine_count=get_subquery(VirtualMachine, 'platform')
    )
    serializer_class = serializers.PlatformSerializer
    filterset_class = filters.PlatformFilter


#
# Devices
#

class DeviceViewSet(CustomFieldModelViewSet):
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'site', 'rack', 'parent_bay',
        'virtual_chassis__master', 'primary_ip4__nat_outside', 'primary_ip6__nat_outside', 'tags',
    )
    filterset_class = filters.DeviceFilter

    def get_serializer_class(self):
        """
        Select the specific serializer based on the request context.

        If the `brief` query param equates to True, return the NestedDeviceSerializer

        If the `exclude` query param includes `config_context` as a value, return the DeviceSerializer

        Else, return the DeviceWithConfigContextSerializer
        """

        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            return serializers.NestedDeviceSerializer

        elif 'config_context' in request.query_params.get('exclude', []):
            return serializers.DeviceSerializer

        return serializers.DeviceWithConfigContextSerializer

    @action(detail=True)
    def graphs(self, request, pk):
        """
        A convenience method for rendering graphs for a particular Device.
        """
        device = get_object_or_404(Device, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_DEVICE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': device})

        return Response(serializer.data)

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

class ConsolePortViewSet(CableTraceMixin, ModelViewSet):
    queryset = ConsolePort.objects.prefetch_related('device', 'connected_endpoint__device', 'cable', 'tags')
    serializer_class = serializers.ConsolePortSerializer
    filterset_class = filters.ConsolePortFilter


class ConsoleServerPortViewSet(CableTraceMixin, ModelViewSet):
    queryset = ConsoleServerPort.objects.prefetch_related('device', 'connected_endpoint__device', 'cable', 'tags')
    serializer_class = serializers.ConsoleServerPortSerializer
    filterset_class = filters.ConsoleServerPortFilter


class PowerPortViewSet(CableTraceMixin, ModelViewSet):
    queryset = PowerPort.objects.prefetch_related(
        'device', '_connected_poweroutlet__device', '_connected_powerfeed', 'cable', 'tags'
    )
    serializer_class = serializers.PowerPortSerializer
    filterset_class = filters.PowerPortFilter


class PowerOutletViewSet(CableTraceMixin, ModelViewSet):
    queryset = PowerOutlet.objects.prefetch_related('device', 'connected_endpoint__device', 'cable', 'tags')
    serializer_class = serializers.PowerOutletSerializer
    filterset_class = filters.PowerOutletFilter


class InterfaceViewSet(CableTraceMixin, ModelViewSet):
    queryset = Interface.objects.prefetch_related(
        'device', '_connected_interface', '_connected_circuittermination', 'cable', 'ip_addresses', 'tags'
    ).filter(
        device__isnull=False
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filters.InterfaceFilter

    @action(detail=True)
    def graphs(self, request, pk):
        """
        A convenience method for rendering graphs for a particular interface.
        """
        interface = get_object_or_404(Interface, pk=pk)
        queryset = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE)
        serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': interface})
        return Response(serializer.data)


class FrontPortViewSet(ModelViewSet):
    queryset = FrontPort.objects.prefetch_related('device__device_type__manufacturer', 'rear_port', 'cable', 'tags')
    serializer_class = serializers.FrontPortSerializer
    filterset_class = filters.FrontPortFilter


class RearPortViewSet(ModelViewSet):
    queryset = RearPort.objects.prefetch_related('device__device_type__manufacturer', 'cable', 'tags')
    serializer_class = serializers.RearPortSerializer
    filterset_class = filters.RearPortFilter


class DeviceBayViewSet(ModelViewSet):
    queryset = DeviceBay.objects.prefetch_related('installed_device').prefetch_related('tags')
    serializer_class = serializers.DeviceBaySerializer
    filterset_class = filters.DeviceBayFilter


class InventoryItemViewSet(ModelViewSet):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer').prefetch_related('tags')
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filters.InventoryItemFilter


#
# Connections
#

class ConsoleConnectionViewSet(ListModelMixin, GenericViewSet):
    queryset = ConsolePort.objects.prefetch_related(
        'device', 'connected_endpoint__device'
    ).filter(
        connected_endpoint__isnull=False
    )
    serializer_class = serializers.ConsolePortSerializer
    filterset_class = filters.ConsoleConnectionFilter


class PowerConnectionViewSet(ListModelMixin, GenericViewSet):
    queryset = PowerPort.objects.prefetch_related(
        'device', 'connected_endpoint__device'
    ).filter(
        _connected_poweroutlet__isnull=False
    )
    serializer_class = serializers.PowerPortSerializer
    filterset_class = filters.PowerConnectionFilter


class InterfaceConnectionViewSet(ListModelMixin, GenericViewSet):
    queryset = Interface.objects.prefetch_related(
        'device', '_connected_interface__device'
    ).filter(
        # Avoid duplicate connections by only selecting the lower PK in a connected pair
        _connected_interface__isnull=False,
        pk__lt=F('_connected_interface')
    )
    serializer_class = serializers.InterfaceConnectionSerializer
    filterset_class = filters.InterfaceConnectionFilter


#
# Cables
#

class CableViewSet(ModelViewSet):
    queryset = Cable.objects.prefetch_related(
        'termination_a', 'termination_b'
    )
    serializer_class = serializers.CableSerializer
    filterset_class = filters.CableFilter


#
# Virtual chassis
#

class VirtualChassisViewSet(ModelViewSet):
    queryset = VirtualChassis.objects.prefetch_related('tags').annotate(
        member_count=Count('members')
    )
    serializer_class = serializers.VirtualChassisSerializer
    filterset_class = filters.VirtualChassisFilter


#
# Power panels
#

class PowerPanelViewSet(ModelViewSet):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        powerfeed_count=Count('powerfeeds')
    )
    serializer_class = serializers.PowerPanelSerializer
    filterset_class = filters.PowerPanelFilter


#
# Power feeds
#

class PowerFeedViewSet(CustomFieldModelViewSet):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack', 'tags')
    serializer_class = serializers.PowerFeedSerializer
    filterset_class = filters.PowerFeedFilter


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
    _device_param = Parameter(
        name='peer_device',
        in_='query',
        description='The name of the peer device',
        required=True,
        type=openapi.TYPE_STRING
    )
    _interface_param = Parameter(
        name='peer_interface',
        in_='query',
        description='The name of the peer interface',
        required=True,
        type=openapi.TYPE_STRING
    )

    def get_view_name(self):
        return "Connected Device Locator"

    @swagger_auto_schema(
        manual_parameters=[_device_param, _interface_param],
        responses={'200': serializers.DeviceSerializer}
    )
    def list(self, request):

        peer_device_name = request.query_params.get(self._device_param.name)
        peer_interface_name = request.query_params.get(self._interface_param.name)

        if not peer_device_name or not peer_interface_name:
            raise MissingFilterException(detail='Request must include "peer_device" and "peer_interface" filters.')

        # Determine local interface from peer interface's connection
        peer_interface = get_object_or_404(Interface, device__name=peer_device_name, name=peer_interface_name)
        local_interface = peer_interface._connected_interface

        if local_interface is None:
            return Response()

        return Response(serializers.DeviceSerializer(local_interface.device, context={'request': request}).data)
