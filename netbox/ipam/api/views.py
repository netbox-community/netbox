from rest_framework.viewsets import ModelViewSet

from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from ipam import filters

from extras.api.views import CustomFieldModelViewSet
from . import serializers


#
# VRFs
#

class VRFViewSet(CustomFieldModelViewSet):
    """
    List and retrieve VRFs
    """
    queryset = VRF.objects.select_related('tenant')
    serializer_class = serializers.VRFSerializer
    filter_class = filters.VRFFilter


#
# Roles
#

class RoleViewSet(ModelViewSet):
    """
    List and retrieve prefix/VLAN roles
    """
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer


#
# RIRs
#

class RIRViewSet(ModelViewSet):
    """
    List and retrieve RIRs
    """
    queryset = RIR.objects.all()
    serializer_class = serializers.RIRSerializer


#
# Aggregates
#

class AggregateViewSet(CustomFieldModelViewSet):
    """
    List and retrieve aggregates
    """
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer
    filter_class = filters.AggregateFilter


#
# Prefixes
#

class PrefixViewSet(CustomFieldModelViewSet):
    """
    List and retrieve prefixes
    """
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer
    filter_class = filters.PrefixFilter


#
# IP addresses
#

class IPAddressViewSet(CustomFieldModelViewSet):
    """
    List and retrieve IP addresses
    """
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')
    serializer_class = serializers.IPAddressSerializer
    filter_class = filters.IPAddressFilter


#
# VLAN groups
#

class VLANGroupViewSet(ModelViewSet):
    """
    List and retrieve VLAN groups
    """
    queryset = VLANGroup.objects.select_related('site')
    serializer_class = serializers.VLANGroupSerializer
    filter_class = filters.VLANGroupFilter


#
# VLANs
#

class VLANViewSet(CustomFieldModelViewSet):
    """
    List and retrieve VLANs
    """
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')
    serializer_class = serializers.VLANSerializer
    filter_class = filters.VLANFilter


#
# Services
#

class ServiceViewSet(ModelViewSet):
    """
    List and retrieve services
    """
    queryset = Service.objects.select_related('device').prefetch_related('ipaddresses')
    serializer_class = serializers.ServiceSerializer
    filter_class = filters.ServiceFilter
