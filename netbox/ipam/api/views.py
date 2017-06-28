from __future__ import unicode_literals

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.conf import settings
from django.shortcuts import get_object_or_404

from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from ipam import filters
from extras.api.views import CustomFieldModelViewSet
from utilities.api import WritableSerializerMixin
from . import serializers


#
# VRFs
#

class VRFViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = VRF.objects.select_related('tenant')
    serializer_class = serializers.VRFSerializer
    write_serializer_class = serializers.WritableVRFSerializer
    filter_class = filters.VRFFilter


#
# RIRs
#

class RIRViewSet(ModelViewSet):
    queryset = RIR.objects.all()
    serializer_class = serializers.RIRSerializer
    filter_class = filters.RIRFilter


#
# Aggregates
#

class AggregateViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer
    write_serializer_class = serializers.WritableAggregateSerializer
    filter_class = filters.AggregateFilter


#
# Roles
#

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer
    filter_class = filters.RoleFilter


#
# Prefixes
#

class PrefixViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer
    write_serializer_class = serializers.WritablePrefixSerializer
    filter_class = filters.PrefixFilter

    @detail_route(url_path='available-ips')
    def available_ips(self, request, pk=None):
        """
        A convenience method for returning available IP addresses within a prefix. By default, the number of IPs
        returned will be equivalent to PAGINATE_COUNT. An arbitrary limit (up to MAX_PAGE_SIZE, if set) may be passed,
        however results will not be paginated.
        """
        prefix = get_object_or_404(Prefix, pk=pk)

        # Determine the maximum amount of IPs to return
        try:
            limit = int(request.query_params.get('limit', settings.PAGINATE_COUNT))
        except ValueError:
            limit = settings.PAGINATE_COUNT
        if settings.MAX_PAGE_SIZE:
            limit = min(limit, settings.MAX_PAGE_SIZE)

        # Calculate available IPs within the prefix
        ip_list = list(prefix.get_available_ips())[:limit]
        serializer = serializers.AvailableIPSerializer(ip_list, many=True, context={
            'request': request,
            'prefix': prefix.prefix,
            'vrf': prefix.vrf,
        })

        return Response(serializer.data)


#
# IP addresses
#

class IPAddressViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')
    serializer_class = serializers.IPAddressSerializer
    write_serializer_class = serializers.WritableIPAddressSerializer
    filter_class = filters.IPAddressFilter


#
# VLAN groups
#

class VLANGroupViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = VLANGroup.objects.select_related('site')
    serializer_class = serializers.VLANGroupSerializer
    write_serializer_class = serializers.WritableVLANGroupSerializer
    filter_class = filters.VLANGroupFilter


#
# VLANs
#

class VLANViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')
    serializer_class = serializers.VLANSerializer
    write_serializer_class = serializers.WritableVLANSerializer
    filter_class = filters.VLANFilter


#
# Services
#

class ServiceViewSet(WritableSerializerMixin, ModelViewSet):
    queryset = Service.objects.select_related('device')
    serializer_class = serializers.ServiceSerializer
    write_serializer_class = serializers.WritableServiceSerializer
    filter_class = filters.ServiceFilter
