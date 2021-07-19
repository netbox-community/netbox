from rest_framework.routers import APIRootView

from extras.api.views import CustomFieldModelViewSet
from ipam import filtersets
from ipam.models import *
from netbox.api.views import ModelViewSet
from utilities.utils import count_related
from . import mixins, serializers


class IPAMRootView(APIRootView):
    """
    IPAM API root view
    """
    def get_view_name(self):
        return 'IPAM'


#
# VRFs
#

class VRFViewSet(CustomFieldModelViewSet):
    queryset = VRF.objects.prefetch_related('tenant').prefetch_related(
        'import_targets', 'export_targets', 'tags'
    ).annotate(
        ipaddress_count=count_related(IPAddress, 'vrf'),
        prefix_count=count_related(Prefix, 'vrf')
    )
    serializer_class = serializers.VRFSerializer
    filterset_class = filtersets.VRFFilterSet


#
# Route targets
#

class RouteTargetViewSet(CustomFieldModelViewSet):
    queryset = RouteTarget.objects.prefetch_related('tenant').prefetch_related('tags')
    serializer_class = serializers.RouteTargetSerializer
    filterset_class = filtersets.RouteTargetFilterSet


#
# RIRs
#

class RIRViewSet(CustomFieldModelViewSet):
    queryset = RIR.objects.annotate(
        aggregate_count=count_related(Aggregate, 'rir')
    )
    serializer_class = serializers.RIRSerializer
    filterset_class = filtersets.RIRFilterSet


#
# Aggregates
#

class AggregateViewSet(CustomFieldModelViewSet):
    queryset = Aggregate.objects.prefetch_related('rir').prefetch_related('tags')
    serializer_class = serializers.AggregateSerializer
    filterset_class = filtersets.AggregateFilterSet


#
# Roles
#

class RoleViewSet(CustomFieldModelViewSet):
    queryset = Role.objects.annotate(
        prefix_count=count_related(Prefix, 'role'),
        vlan_count=count_related(VLAN, 'role')
    )
    serializer_class = serializers.RoleSerializer
    filterset_class = filtersets.RoleFilterSet


#
# Prefixes
#

class PrefixViewSet(mixins.AvailableIPsMixin, mixins.AvailablePrefixesMixin, CustomFieldModelViewSet):
    queryset = Prefix.objects.prefetch_related(
        'site', 'vrf__tenant', 'tenant', 'vlan', 'role', 'tags'
    )
    serializer_class = serializers.PrefixSerializer
    filterset_class = filtersets.PrefixFilterSet

    parent_model = Prefix  # AvailableIPsMixin

    def get_serializer_class(self):
        if self.action == "available_prefixes" and self.request.method == "POST":
            return serializers.PrefixLengthSerializer
        return super().get_serializer_class()


#
# IP ranges
#

class IPRangeViewSet(mixins.AvailableIPsMixin, CustomFieldModelViewSet):
    queryset = IPRange.objects.prefetch_related('vrf', 'role', 'tenant', 'tags')
    serializer_class = serializers.IPRangeSerializer
    filterset_class = filtersets.IPRangeFilterSet

    parent_model = IPRange  # AvailableIPsMixin


#
# IP addresses
#

class IPAddressViewSet(CustomFieldModelViewSet):
    queryset = IPAddress.objects.prefetch_related(
        'vrf__tenant', 'tenant', 'nat_inside', 'nat_outside', 'tags', 'assigned_object'
    )
    serializer_class = serializers.IPAddressSerializer
    filterset_class = filtersets.IPAddressFilterSet


#
# VLAN groups
#

class VLANGroupViewSet(CustomFieldModelViewSet):
    queryset = VLANGroup.objects.annotate(
        vlan_count=count_related(VLAN, 'group')
    )
    serializer_class = serializers.VLANGroupSerializer
    filterset_class = filtersets.VLANGroupFilterSet


#
# VLANs
#

class VLANViewSet(CustomFieldModelViewSet):
    queryset = VLAN.objects.prefetch_related(
        'site', 'group', 'tenant', 'role', 'tags'
    ).annotate(
        prefix_count=count_related(Prefix, 'vlan')
    )
    serializer_class = serializers.VLANSerializer
    filterset_class = filtersets.VLANFilterSet


#
# Services
#

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.prefetch_related(
        'device', 'virtual_machine', 'tags', 'ipaddresses'
    )
    serializer_class = serializers.ServiceSerializer
    filterset_class = filtersets.ServiceFilterSet
