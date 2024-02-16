from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ViewSet

from circuits.models import Circuit
from dcim import filtersets
from dcim.constants import CABLE_TRACE_SVG_DEFAULT_WIDTH
from dcim.models import *
from dcim.svg import CableTraceSVG
from extras.api.mixins import ConfigContextQuerySetMixin, RenderConfigMixin
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.pagination import StripCountAnnotationsPaginator
from netbox.api.viewsets import NetBoxModelViewSet, MPTTLockedMixin
from netbox.api.viewsets.mixins import SequentialBulkCreatesMixin
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model
from utilities.query_functions import CollateAsChar
from utilities.utils import count_related
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

        # Render SVG image if requested
        if request.GET.get('render', None) == 'svg':
            try:
                width = int(request.GET.get('width', CABLE_TRACE_SVG_DEFAULT_WIDTH))
            except (ValueError, TypeError):
                width = CABLE_TRACE_SVG_DEFAULT_WIDTH
            drawing = CableTraceSVG(obj, base_url=request.build_absolute_uri('/'), width=width)
            return HttpResponse(drawing.render().tostring(), content_type='image/svg+xml')

        # Serialize path objects, iterating over each three-tuple in the path
        for near_ends, cable, far_ends in obj.trace():
            if near_ends:
                serializer_a = get_serializer_for_model(near_ends[0], prefix=NESTED_SERIALIZER_PREFIX)
                near_ends = serializer_a(near_ends, many=True, context={'request': request}).data
            else:
                # Path is split; stop here
                break
            if cable:
                cable = serializers.TracedCableSerializer(cable[0], context={'request': request}).data
            if far_ends:
                serializer_b = get_serializer_for_model(far_ends[0], prefix=NESTED_SERIALIZER_PREFIX)
                far_ends = serializer_b(far_ends, many=True, context={'request': request}).data

            path.append((near_ends, cable, far_ends))

        return Response(path)


class PassThroughPortMixin(object):

    @action(detail=True, url_path='paths')
    def paths(self, request, pk):
        """
        Return all CablePaths which traverse a given pass-through port.
        """
        obj = get_object_or_404(self.queryset, pk=pk)
        cablepaths = CablePath.objects.filter(_nodes__contains=obj)
        serializer = serializers.CablePathSerializer(cablepaths, context={'request': request}, many=True)

        return Response(serializer.data)


#
# Regions
#

class RegionViewSet(MPTTLockedMixin, NetBoxModelViewSet):
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

class SiteGroupViewSet(MPTTLockedMixin, NetBoxModelViewSet):
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

class SiteViewSet(NetBoxModelViewSet):
    queryset = Site.objects.all()
    serializer_class = serializers.SiteSerializer
    filterset_class = filtersets.SiteFilterSet


#
# Locations
#

class LocationViewSet(MPTTLockedMixin, NetBoxModelViewSet):
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
    )
    serializer_class = serializers.LocationSerializer
    filterset_class = filtersets.LocationFilterSet


#
# Rack roles
#

class RackRoleViewSet(NetBoxModelViewSet):
    queryset = RackRole.objects.all()
    serializer_class = serializers.RackRoleSerializer
    filterset_class = filtersets.RackRoleFilterSet


#
# Racks
#

class RackViewSet(NetBoxModelViewSet):
    queryset = Rack.objects.all()
    serializer_class = serializers.RackSerializer
    filterset_class = filtersets.RackFilterSet

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
            # Determine attributes for highlighting devices (if any)
            highlight_params = []
            for param in request.GET.getlist('highlight'):
                try:
                    highlight_params.append(param.split(':', 1))
                except ValueError:
                    pass

            # Render and return the elevation as an SVG drawing with the correct content type
            drawing = rack.get_elevation_svg(
                face=data['face'],
                user=request.user,
                unit_width=data['unit_width'],
                unit_height=data['unit_height'],
                legend_width=data['legend_width'],
                include_images=data['include_images'],
                base_url=request.build_absolute_uri('/'),
                highlight_params=highlight_params
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

class RackReservationViewSet(NetBoxModelViewSet):
    queryset = RackReservation.objects.all()
    serializer_class = serializers.RackReservationSerializer
    filterset_class = filtersets.RackReservationFilterSet


#
# Manufacturers
#

class ManufacturerViewSet(NetBoxModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer
    filterset_class = filtersets.ManufacturerFilterSet


#
# Device/module types
#

class DeviceTypeViewSet(NetBoxModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = serializers.DeviceTypeSerializer
    filterset_class = filtersets.DeviceTypeFilterSet


class ModuleTypeViewSet(NetBoxModelViewSet):
    queryset = ModuleType.objects.all()
    serializer_class = serializers.ModuleTypeSerializer
    filterset_class = filtersets.ModuleTypeFilterSet


#
# Device type components
#

class ConsolePortTemplateViewSet(NetBoxModelViewSet):
    queryset = ConsolePortTemplate.objects.all()
    serializer_class = serializers.ConsolePortTemplateSerializer
    filterset_class = filtersets.ConsolePortTemplateFilterSet


class ConsoleServerPortTemplateViewSet(NetBoxModelViewSet):
    queryset = ConsoleServerPortTemplate.objects.all()
    serializer_class = serializers.ConsoleServerPortTemplateSerializer
    filterset_class = filtersets.ConsoleServerPortTemplateFilterSet


class PowerPortTemplateViewSet(NetBoxModelViewSet):
    queryset = PowerPortTemplate.objects.all()
    serializer_class = serializers.PowerPortTemplateSerializer
    filterset_class = filtersets.PowerPortTemplateFilterSet


class PowerOutletTemplateViewSet(NetBoxModelViewSet):
    queryset = PowerOutletTemplate.objects.all()
    serializer_class = serializers.PowerOutletTemplateSerializer
    filterset_class = filtersets.PowerOutletTemplateFilterSet


class InterfaceTemplateViewSet(NetBoxModelViewSet):
    queryset = InterfaceTemplate.objects.all()
    serializer_class = serializers.InterfaceTemplateSerializer
    filterset_class = filtersets.InterfaceTemplateFilterSet


class FrontPortTemplateViewSet(NetBoxModelViewSet):
    queryset = FrontPortTemplate.objects.all()
    serializer_class = serializers.FrontPortTemplateSerializer
    filterset_class = filtersets.FrontPortTemplateFilterSet


class RearPortTemplateViewSet(NetBoxModelViewSet):
    queryset = RearPortTemplate.objects.all()
    serializer_class = serializers.RearPortTemplateSerializer
    filterset_class = filtersets.RearPortTemplateFilterSet


class ModuleBayTemplateViewSet(NetBoxModelViewSet):
    queryset = ModuleBayTemplate.objects.all()
    serializer_class = serializers.ModuleBayTemplateSerializer
    filterset_class = filtersets.ModuleBayTemplateFilterSet


class DeviceBayTemplateViewSet(NetBoxModelViewSet):
    queryset = DeviceBayTemplate.objects.all()
    serializer_class = serializers.DeviceBayTemplateSerializer
    filterset_class = filtersets.DeviceBayTemplateFilterSet


class InventoryItemTemplateViewSet(MPTTLockedMixin, NetBoxModelViewSet):
    queryset = InventoryItemTemplate.objects.all()
    serializer_class = serializers.InventoryItemTemplateSerializer
    filterset_class = filtersets.InventoryItemTemplateFilterSet


#
# Device roles
#

class DeviceRoleViewSet(NetBoxModelViewSet):
    queryset = DeviceRole.objects.all()
    serializer_class = serializers.DeviceRoleSerializer
    filterset_class = filtersets.DeviceRoleFilterSet


#
# Platforms
#

class PlatformViewSet(NetBoxModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = serializers.PlatformSerializer
    filterset_class = filtersets.PlatformFilterSet


#
# Devices/modules
#

class DeviceViewSet(
    SequentialBulkCreatesMixin,
    ConfigContextQuerySetMixin,
    RenderConfigMixin,
    NetBoxModelViewSet
):
    queryset = Device.objects.prefetch_related(
        'parent_bay',  # Referenced by DeviceSerializer.get_parent_device()
    )
    filterset_class = filtersets.DeviceFilterSet
    pagination_class = StripCountAnnotationsPaginator

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


class VirtualDeviceContextViewSet(NetBoxModelViewSet):
    queryset = VirtualDeviceContext.objects.all()
    serializer_class = serializers.VirtualDeviceContextSerializer
    filterset_class = filtersets.VirtualDeviceContextFilterSet


class ModuleViewSet(NetBoxModelViewSet):
    queryset = Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    filterset_class = filtersets.ModuleFilterSet


#
# Device components
#

class ConsolePortViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = ConsolePort.objects.prefetch_related(
        '_path', 'cable__terminations',
    )
    serializer_class = serializers.ConsolePortSerializer
    filterset_class = filtersets.ConsolePortFilterSet


class ConsoleServerPortViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = ConsoleServerPort.objects.prefetch_related(
        '_path', 'cable__terminations',
    )
    serializer_class = serializers.ConsoleServerPortSerializer
    filterset_class = filtersets.ConsoleServerPortFilterSet


class PowerPortViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = PowerPort.objects.prefetch_related(
        '_path', 'cable__terminations',
    )
    serializer_class = serializers.PowerPortSerializer
    filterset_class = filtersets.PowerPortFilterSet


class PowerOutletViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = PowerOutlet.objects.prefetch_related(
        '_path', 'cable__terminations',
    )
    serializer_class = serializers.PowerOutletSerializer
    filterset_class = filtersets.PowerOutletFilterSet


class InterfaceViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = Interface.objects.prefetch_related(
        '_path', 'cable__terminations',
        'l2vpn_terminations',  # Referenced by InterfaceSerializer.l2vpn_termination
        'ip_addresses',  # Referenced by Interface.count_ipaddresses()
        'fhrp_group_assignments',  # Referenced by Interface.count_fhrp_groups()
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filtersets.InterfaceFilterSet

    def get_bulk_destroy_queryset(self):
        # Ensure child interfaces are deleted prior to their parents
        return self.get_queryset().order_by('device', 'parent', CollateAsChar('_name'))


class FrontPortViewSet(PassThroughPortMixin, NetBoxModelViewSet):
    queryset = FrontPort.objects.prefetch_related(
        'cable__terminations',
    )
    serializer_class = serializers.FrontPortSerializer
    filterset_class = filtersets.FrontPortFilterSet


class RearPortViewSet(PassThroughPortMixin, NetBoxModelViewSet):
    queryset = RearPort.objects.prefetch_related(
        'cable__terminations',
    )
    serializer_class = serializers.RearPortSerializer
    filterset_class = filtersets.RearPortFilterSet


class ModuleBayViewSet(NetBoxModelViewSet):
    queryset = ModuleBay.objects.all()
    serializer_class = serializers.ModuleBaySerializer
    filterset_class = filtersets.ModuleBayFilterSet


class DeviceBayViewSet(NetBoxModelViewSet):
    queryset = DeviceBay.objects.all()
    serializer_class = serializers.DeviceBaySerializer
    filterset_class = filtersets.DeviceBayFilterSet


class InventoryItemViewSet(MPTTLockedMixin, NetBoxModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer
    filterset_class = filtersets.InventoryItemFilterSet


#
# Device component roles
#

class InventoryItemRoleViewSet(NetBoxModelViewSet):
    queryset = InventoryItemRole.objects.all()
    serializer_class = serializers.InventoryItemRoleSerializer
    filterset_class = filtersets.InventoryItemRoleFilterSet


#
# Cables
#

class CableViewSet(NetBoxModelViewSet):
    queryset = Cable.objects.prefetch_related('terminations__termination')
    serializer_class = serializers.CableSerializer
    filterset_class = filtersets.CableFilterSet


class CableTerminationViewSet(NetBoxModelViewSet):
    metadata_class = ContentTypeMetadata
    queryset = CableTermination.objects.all()
    serializer_class = serializers.CableTerminationSerializer
    filterset_class = filtersets.CableTerminationFilterSet


#
# Virtual chassis
#

class VirtualChassisViewSet(NetBoxModelViewSet):
    queryset = VirtualChassis.objects.all()
    serializer_class = serializers.VirtualChassisSerializer
    filterset_class = filtersets.VirtualChassisFilterSet


#
# Power panels
#

class PowerPanelViewSet(NetBoxModelViewSet):
    queryset = PowerPanel.objects.all()
    serializer_class = serializers.PowerPanelSerializer
    filterset_class = filtersets.PowerPanelFilterSet


#
# Power feeds
#

class PowerFeedViewSet(PathEndpointMixin, NetBoxModelViewSet):
    queryset = PowerFeed.objects.prefetch_related(
        '_path', 'cable__terminations',
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
    _device_param = OpenApiParameter(
        name='peer_device',
        location='query',
        description='The name of the peer device',
        required=True,
        type=OpenApiTypes.STR
    )
    _interface_param = OpenApiParameter(
        name='peer_interface',
        location='query',
        description='The name of the peer interface',
        required=True,
        type=OpenApiTypes.STR
    )
    serializer_class = serializers.DeviceSerializer

    def get_view_name(self):
        return "Connected Device Locator"

    @extend_schema(
        parameters=[_device_param, _interface_param],
        responses={200: serializers.DeviceSerializer}
    )
    def list(self, request):

        peer_device_name = request.query_params.get(self._device_param.name)
        peer_interface_name = request.query_params.get(self._interface_param.name)

        if not peer_device_name or not peer_interface_name:
            raise MissingFilterException(detail='Request must include "peer_device" and "peer_interface" filters.')

        # Determine local endpoint from peer interface's connection
        peer_device = get_object_or_404(
            Device.objects.restrict(request.user, 'view'),
            name=peer_device_name
        )
        peer_interface = get_object_or_404(
            Interface.objects.restrict(request.user, 'view'),
            device=peer_device,
            name=peer_interface_name
        )
        endpoints = peer_interface.connected_endpoints

        # If an Interface, return the parent device
        if endpoints and type(endpoints[0]) is Interface:
            device = get_object_or_404(
                Device.objects.restrict(request.user, 'view'),
                pk=endpoints[0].device_id
            )
            return Response(serializers.DeviceSerializer(device, context={'request': request}).data)

        # Connected endpoint is none or not an Interface
        raise Http404
