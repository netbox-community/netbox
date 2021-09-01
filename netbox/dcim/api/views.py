import socket
from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ViewSet

from circuits.models import Circuit
from dcim import filtersets
from dcim.models import *
from extras.api.views import ConfigContextQuerySetMixin, CustomFieldModelViewSet
from ipam.models import Prefix, VLAN
from netbox.api.views import ModelViewSet
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.exceptions import ServiceUnavailable
from netbox.api.metadata import ContentTypeMetadata
from utilities.api import get_serializer_for_model
from utilities.utils import count_related, decode_dict
from virtualization.models import VirtualMachine
from . import serializers
from .exceptions import MissingFilterException


class DCIMRootView(APIRootView):
    """
    DCIM API root view
    """
    def get_view_name(self):
        return 'DCIM'


# Mixins

class PathEndpointMixin(object):

    @action(detail=True, url_path='trace')
    def trace(self, request, pk):
        """
        Trace a complete cable path and return each segment as a three-tuple of (termination, cable, termination).
        """
        obj = get_object_or_404(self.queryset, pk=pk)

        # Initialize the path array
        path = []

        if request.GET.get('render', None) == 'svg':
            # Render SVG
            try:
                width = min(int(request.GET.get('width')), 1600)
            except (ValueError, TypeError):
                width = None
            drawing = obj.get_trace_svg(
                base_url=request.build_absolute_uri('/'),
                width=width
            )
            return HttpResponse(drawing.tostring(), content_type='image/svg+xml')

        for near_end, cable, far_end in obj.trace():
            if near_end is None:
                # Split paths
                break

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


class PassThroughPortMixin(object):

    @action(detail=True, url_path='paths')
    def paths(self, request, pk):
        """
        Return all CablePaths which traverse a given pass-through port.
        """
        obj = get_object_or_404(self.queryset, pk=pk)
        cablepaths = CablePath.objects.filter(path__contains=obj).prefetch_related('origin', 'destination')
        serializer = serializers.CablePathSerializer(cablepaths, context={'request': request}, many=True)

        return Response(serializer.data)


#
# Regions
#

class RegionViewSet(CustomFieldModelViewSet):
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    serializer_class = serializers.RegionSerializer
    filterset_class = filtersets.RegionFilterSet


#
# Site groups
#

class SiteGroupViewSet(CustomFieldModelViewSet):
    queryset = SiteGroup.objects.add_related_count(
        SiteGroup.objects.all(),
        Site,
        'group',
        'site_count',
        cumulative=True
    )
    serializer_class = serializers.SiteGroupSerializer
    filterset_class = filtersets.SiteGroupFilterSet


#
# Sites
#

class SiteViewSet(CustomFieldModelViewSet):
    queryset = Site.objects.prefetch_related(
        'region', 'tenant', 'tags'
    ).annotate(
        device_count=count_related(Device, 'site'),
        rack_count=count_related(Rack, 'site'),
        prefix_count=count_related(Prefix, 'site'),
        vlan_count=count_related(VLAN, 'site'),
        circuit_count=count_related(Circuit, 'terminations__site'),
        virtualmachine_count=count_related(VirtualMachine, 'cluster__site')
    )
    serializer_class = serializers.SiteSerializer
    filterset_class = filtersets.SiteFilterSet


#
# Locations
#

class LocationViewSet(CustomFieldModelViewSet):
    queryset = Location.objects.add_related_count(
        Location.objects.add_related_count(
            Location.objects.all(),
            Device,
            'location',
            'device_count',
            cumulative=True
        ),
        Rack,
        'location',
        'rack_count',
        cumulative=True
    ).prefetch_related('site')
    serializer_class = serializers.LocationSerializer
    filterset_class = filtersets.LocationFilterSet


#
# Rack roles
#

class RackRoleViewSet(CustomFieldModelViewSet):
    queryset = RackRole.objects.annotate(
        rack_count=count_related(Rack, 'role')
    )
    serializer_class = serializers.RackRoleSerializer
    filterset_class = filtersets.RackRoleFilterSet


#
# Racks
#

class RackViewSet(CustomFieldModelViewSet):
    queryset = Rack.objects.prefetch_related(
        'site', 'location', 'role', 'tenant', 'tags'
    ).annotate(
        device_count=count_related(Device, 'rack'),
        powerfeed_count=count_related(PowerFeed, 'rack')
    )
    serializer_class = serializers.RackSerializer
    filterset_class = filtersets.RackFilterSet

    @swagger_auto_schema(
        responses={200: serializers.RackUnitSerializer(many=True)},
        query_serializer=serializers.RackElevationDetailFilterSerializer
    )
    @action(detail=True)
    def elevation(self, request, pk=None):
        """
        Rack elevation representing the list of rack units. Also supports rendering the elevation as an SVG.
        """
        rack = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.RackElevationDetailFilterSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        data = serializer.validated_data

        if data['render'] == 'svg':
            # Render and return the elevation as an SVG drawing with the correct content type
            drawing = rack.get_elevation_svg(
                face=data['face'],
                user=request.user,
                unit_width=data['unit_width'],
                unit_height=data['unit_height'],
                legend_width=data['legend_width'],
                include_images=data['include_images'],
                base_url=request.build_absolute_uri('/')
            )
            return HttpResponse(drawing.tostring(), content_type='image/svg+xml')

        else:
            # Return a JSON representation of the rack units in the elevation
            elevation = rack.get_rack_units(
                face=data['face'],
                user=request.user,
                exclude=data['exclude'],
                expand_devices=data['expand_devices']
            )

            # Enable filtering rack units by ID
            q = data['q']
            if q:
                elevation = [u for u in elevation if q in str(u['id']) or q in str(u['name'])]

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
    filterset_class = filtersets.RackReservationFilterSet


#
# Manufacturers
#

class ManufacturerViewSet(CustomFieldModelViewSet):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
        inventoryitem_count=count_related(InventoryItem, 'manufacturer'),
        platform_count=count_related(Platform, 'manufacturer')
    )
    serializer_class = serializers.ManufacturerSerializer
    filterset_class = filtersets.ManufacturerFilterSet


#
# Device types
#

class DeviceTypeViewSet(CustomFieldModelViewSet):
    queryset = DeviceType.objects.prefetch_related('manufacturer', 'tags').annotate(
        device_count=count_related(Device, 'device_type')
    )
    serializer_class = serializers.DeviceTypeSerializer
    filterset_class = filtersets.DeviceTypeFilterSet
    brief_prefetch_fields = ['manufacturer']


#
# Device type components
#

class ConsolePortTemplateViewSet(ModelViewSet):
    queryset = ConsolePortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.ConsolePortTemplateSerializer
    filterset_class = filtersets.ConsolePortTemplateFilterSet


class ConsoleServerPortTemplateViewSet(ModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    filterset_class = filtersets.ConsoleServerPortTemplateFilterSet


class PowerPortTemplateViewSet(ModelViewSet):
    queryset = PowerPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.PowerPortTemplateSerializer
    filterset_class = filtersets.PowerPortTemplateFilterSet


class PowerOutletTemplateViewSet(ModelViewSet):
    queryset = PowerOutletTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.PowerOutletTemplateSerializer
    filterset_class = filtersets.PowerOutletTemplateFilterSet


class InterfaceTemplateViewSet(ModelViewSet):
    queryset = InterfaceTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.InterfaceTemplateSerializer
    filterset_class = filtersets.InterfaceTemplateFilterSet


class FrontPortTemplateViewSet(ModelViewSet):
    queryset = FrontPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.FrontPortTemplateSerializer
    filterset_class = filtersets.FrontPortTemplateFilterSet


class RearPortTemplateViewSet(ModelViewSet):
    queryset = RearPortTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.RearPortTemplateSerializer
    filterset_class = filtersets.RearPortTemplateFilterSet


class DeviceBayTemplateViewSet(ModelViewSet):
    queryset = DeviceBayTemplate.objects.prefetch_related('device_type__manufacturer')
    serializer_class = serializers.DeviceBayTemplateSerializer
    filterset_class = filtersets.DeviceBayTemplateFilterSet


#
# Device roles
#

class DeviceRoleViewSet(CustomFieldModelViewSet):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
        virtualmachine_count=count_related(VirtualMachine, 'role')
    )
    serializer_class = serializers.DeviceRoleSerializer
    filterset_class = filtersets.DeviceRoleFilterSet


#
# Platforms
#

class PlatformViewSet(CustomFieldModelViewSet):
    queryset = Platform.objects.annotate(
        device_count=count_related(Device, 'platform'),
        virtualmachine_count=count_related(VirtualMachine, 'platform')
    )
    serializer_class = serializers.PlatformSerializer
    filterset_class = filtersets.PlatformFilterSet


#
# Devices
#

class DeviceViewSet(ConfigContextQuerySetMixin, CustomFieldModelViewSet):
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'site', 'location', 'rack', 'parent_bay',
        'virtual_chassis__master', 'primary_ip4__nat_outside', 'primary_ip6__nat_outside', 'tags',
    )
    filterset_class = filtersets.DeviceFilterSet

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

    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                name='method',
                in_='query',
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={'200': serializers.DeviceNAPALMSerializer}
    )
    @action(detail=True, url_path='napalm')
    def napalm(self, request, pk):
        """
        Execute a NAPALM method on a Device
        """
        device = get_object_or_404(self.queryset, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable("This device does not have a primary IP address configured.")
        if device.platform is None:
            raise ServiceUnavailable("No platform is configured for this device.")
        if not device.platform.napalm_driver:
            raise ServiceUnavailable(f"No NAPALM driver is configured for this device's platform: {device.platform}.")

        # Check for primary IP address from NetBox object
        if device.primary_ip:
            host = str(device.primary_ip.address.ip)
        else:
            # Raise exception for no IP address and no Name if device.name does not exist
            if not device.name:
                raise ServiceUnavailable(
                    "This device does not have a primary IP address or device name to lookup configured."
                )
            try:
                # Attempt to complete a DNS name resolution if no primary_ip is set
                host = socket.gethostbyname(device.name)
            except socket.gaierror:
                # Name lookup failure
                raise ServiceUnavailable(
                    f"Name lookup failure, unable to resolve IP address for {device.name}. Please set Primary IP or "
                    f"setup name resolution.")

        # Check that NAPALM is installed
        try:
            import napalm
            from napalm.base.exceptions import ModuleImportError
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'napalm':
                raise ServiceUnavailable("NAPALM is not installed. Please see the documentation for instructions.")
            raise e

        # Validate the configured driver
        try:
            driver = napalm.get_network_driver(device.platform.napalm_driver)
        except ModuleImportError:
            raise ServiceUnavailable("NAPALM driver for platform {} not found: {}.".format(
                device.platform, device.platform.napalm_driver
            ))

        # Verify user permission
        if not request.user.has_perm('dcim.napalm_read_device'):
            return HttpResponseForbidden()

        napalm_methods = request.GET.getlist('method')
        response = OrderedDict([(m, None) for m in napalm_methods])
        username = settings.NAPALM_USERNAME
        password = settings.NAPALM_PASSWORD
        optional_args = settings.NAPALM_ARGS.copy()
        if device.platform.napalm_args is not None:
            optional_args.update(device.platform.napalm_args)

        # Update NAPALM parameters according to the request headers
        for header in request.headers:
            if header[:9].lower() != 'x-napalm-':
                continue

            key = header[9:]
            if key.lower() == 'username':
                username = request.headers[header]
            elif key.lower() == 'password':
                password = request.headers[header]
            elif key:
                optional_args[key.lower()] = request.headers[header]

        # Connect to the device
        d = driver(
            hostname=host,
            username=username,
            password=password,
            timeout=settings.NAPALM_TIMEOUT,
            optional_args=optional_args
        )
        try:
            d.open()
        except Exception as e:
            raise ServiceUnavailable("Error connecting to the device at {}: {}".format(host, e))

        # Validate and execute each specified NAPALM method
        for method in napalm_methods:
            if not hasattr(driver, method):
                response[method] = {'error': 'Unknown NAPALM method'}
                continue
            if not method.startswith('get_'):
                response[method] = {'error': 'Only get_* NAPALM methods are supported'}
                continue
            try:
                response[method] = decode_dict(getattr(d, method)())
            except NotImplementedError:
                response[method] = {'error': 'Method {} not implemented for NAPALM driver {}'.format(method, driver)}
            except Exception as e:
                response[method] = {'error': 'Method {} failed: {}'.format(method, e)}
        d.close()

        return Response(response)


#
# Device components
#

class ConsolePortViewSet(PathEndpointMixin, ModelViewSet):
    queryset = ConsolePort.objects.prefetch_related('device', '_path__destination', 'cable', '_cable_peer', 'tags')
    serializer_class = serializers.ConsolePortSerializer
    filterset_class = filtersets.ConsolePortFilterSet
    brief_prefetch_fields = ['device']


class ConsoleServerPortViewSet(PathEndpointMixin, ModelViewSet):
    queryset = ConsoleServerPort.objects.prefetch_related(
        'device', '_path__destination', 'cable', '_cable_peer', 'tags'
    )
    serializer_class = serializers.ConsoleServerPortSerializer
    filterset_class = filtersets.ConsoleServerPortFilterSet
    brief_prefetch_fields = ['device']


class PowerPortViewSet(PathEndpointMixin, ModelViewSet):
    queryset = PowerPort.objects.prefetch_related('device', '_path__destination', 'cable', '_cable_peer', 'tags')
    serializer_class = serializers.PowerPortSerializer
    filterset_class = filtersets.PowerPortFilterSet
    brief_prefetch_fields = ['device']


class PowerOutletViewSet(PathEndpointMixin, ModelViewSet):
    queryset = PowerOutlet.objects.prefetch_related('device', '_path__destination', 'cable', '_cable_peer', 'tags')
    serializer_class = serializers.PowerOutletSerializer
    filterset_class = filtersets.PowerOutletFilterSet
    brief_prefetch_fields = ['device']


class InterfaceViewSet(PathEndpointMixin, ModelViewSet):
    queryset = Interface.objects.prefetch_related(
        'device', 'parent', 'lag', '_path__destination', 'cable', '_cable_peer', 'ip_addresses', 'tags'
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filtersets.InterfaceFilterSet
    brief_prefetch_fields = ['device']


class FrontPortViewSet(PassThroughPortMixin, ModelViewSet):
    queryset = FrontPort.objects.prefetch_related('device__device_type__manufacturer', 'rear_port', 'cable', 'tags')
    serializer_class = serializers.FrontPortSerializer
    filterset_class = filtersets.FrontPortFilterSet
    brief_prefetch_fields = ['device']


class RearPortViewSet(PassThroughPortMixin, ModelViewSet):
    queryset = RearPort.objects.prefetch_related('device__device_type__manufacturer', 'cable', 'tags')
    serializer_class = serializers.RearPortSerializer
    filterset_class = filtersets.RearPortFilterSet
    brief_prefetch_fields = ['device']


class DeviceBayViewSet(ModelViewSet):
    queryset = DeviceBay.objects.prefetch_related('installed_device').prefetch_related('tags')
    serializer_class = serializers.DeviceBaySerializer
    filterset_class = filtersets.DeviceBayFilterSet
    brief_prefetch_fields = ['device']


class InventoryItemViewSet(ModelViewSet):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer').prefetch_related('tags')
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filtersets.InventoryItemFilterSet
    brief_prefetch_fields = ['device']


#
# Cables
#

class CableViewSet(ModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = Cable.objects.prefetch_related(
        'termination_a', 'termination_b'
    )
    serializer_class = serializers.CableSerializer
    filterset_class = filtersets.CableFilterSet


#
# Virtual chassis
#

class VirtualChassisViewSet(ModelViewSet):
    queryset = VirtualChassis.objects.prefetch_related('tags').annotate(
        member_count=count_related(Device, 'virtual_chassis')
    )
    serializer_class = serializers.VirtualChassisSerializer
    filterset_class = filtersets.VirtualChassisFilterSet
    brief_prefetch_fields = ['master']


#
# Power panels
#

class PowerPanelViewSet(ModelViewSet):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'location'
    ).annotate(
        powerfeed_count=count_related(PowerFeed, 'power_panel')
    )
    serializer_class = serializers.PowerPanelSerializer
    filterset_class = filtersets.PowerPanelFilterSet


#
# Power feeds
#

class PowerFeedViewSet(PathEndpointMixin, CustomFieldModelViewSet):
    queryset = PowerFeed.objects.prefetch_related(
        'power_panel', 'rack', '_path__destination', 'cable', '_cable_peer', 'tags'
    )
    serializer_class = serializers.PowerFeedSerializer
    filterset_class = filtersets.PowerFeedFilterSet


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
        peer_interface = get_object_or_404(
            Interface.objects.all(),
            device__name=peer_device_name,
            name=peer_interface_name
        )
        local_interface = peer_interface.connected_endpoint

        if local_interface is None:
            return Response()

        return Response(serializers.DeviceSerializer(local_interface.device, context={'request': request}).data)
