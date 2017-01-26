from rest_framework.viewsets import ModelViewSet

from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from ipam import filters

from extras.api.views import CustomFieldModelViewSet
from . import serializers


#
# VRFs
#

class VRFViewSet(CustomFieldModelViewSet):
    queryset = VRF.objects.select_related('tenant')
    serializer_class = serializers.VRFSerializer
    filter_class = filters.VRFFilter


#
# Roles
#

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer


#
# RIRs
#

class RIRViewSet(ModelViewSet):
    queryset = RIR.objects.all()
    serializer_class = serializers.RIRSerializer


#
# Aggregates
#

class AggregateViewSet(CustomFieldModelViewSet):
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer
    filter_class = filters.AggregateFilter


#
# Prefixes
#

class PrefixViewSet(CustomFieldModelViewSet):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer
    filter_class = filters.PrefixFilter


#
# IP addresses
#

class IPAddressViewSet(CustomFieldModelViewSet):
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')
    serializer_class = serializers.IPAddressSerializer
    filter_class = filters.IPAddressFilter


#
# VLAN groups
#

class VLANGroupViewSet(ModelViewSet):
    queryset = VLANGroup.objects.select_related('site')
    serializer_class = serializers.VLANGroupSerializer
    filter_class = filters.VLANGroupFilter


#
# VLANs
#

class VLANViewSet(CustomFieldModelViewSet):
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')
    serializer_class = serializers.VLANSerializer
    filter_class = filters.VLANFilter


#
# Services
#

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.select_related('device').prefetch_related('ipaddresses')
    serializer_class = serializers.ServiceSerializer
    filter_class = filters.ServiceFilter
