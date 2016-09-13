from rest_framework import generics

from ipam.models import VRF, Role, RIR, Aggregate, Prefix, IPAddress, VLAN, VLANGroup
from ipam import filters

from extras.api.views import CustomFieldModelAPIView
from . import serializers


#
# VRFs
#

class VRFListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List all VRFs
    """
    queryset = VRF.objects.select_related('tenant').prefetch_related('custom_field_values__field')
    serializer_class = serializers.VRFSerializer
    filter_class = filters.VRFFilter


class VRFDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single VRF
    """
    queryset = VRF.objects.select_related('tenant').prefetch_related('custom_field_values__field')
    serializer_class = serializers.VRFSerializer


#
# Roles
#

class RoleListView(generics.ListAPIView):
    """
    List all roles
    """
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer


class RoleDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single role
    """
    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer


#
# RIRs
#

class RIRListView(generics.ListAPIView):
    """
    List all RIRs
    """
    queryset = RIR.objects.all()
    serializer_class = serializers.RIRSerializer


class RIRDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single RIR
    """
    queryset = RIR.objects.all()
    serializer_class = serializers.RIRSerializer


#
# Aggregates
#

class AggregateListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List aggregates (filterable)
    """
    queryset = Aggregate.objects.select_related('rir').prefetch_related('custom_field_values__field')
    serializer_class = serializers.AggregateSerializer
    filter_class = filters.AggregateFilter


class AggregateDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single aggregate
    """
    queryset = Aggregate.objects.select_related('rir').prefetch_related('custom_field_values__field')
    serializer_class = serializers.AggregateSerializer


#
# Prefixes
#

class PrefixListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List prefixes (filterable)
    """
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.PrefixSerializer
    filter_class = filters.PrefixFilter


class PrefixDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single prefix
    """
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.PrefixSerializer


#
# IP addresses
#

class IPAddressListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List IP addresses (filterable)
    """
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')\
        .prefetch_related('nat_outside', 'custom_field_values__field')
    serializer_class = serializers.IPAddressSerializer
    filter_class = filters.IPAddressFilter


class IPAddressDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single IP address
    """
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')\
        .prefetch_related('nat_outside', 'custom_field_values__field')
    serializer_class = serializers.IPAddressSerializer


#
# VLAN groups
#

class VLANGroupListView(generics.ListAPIView):
    """
    List all VLAN groups
    """
    queryset = VLANGroup.objects.select_related('site')
    serializer_class = serializers.VLANGroupSerializer
    filter_class = filters.VLANGroupFilter


class VLANGroupDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single VLAN group
    """
    queryset = VLANGroup.objects.select_related('site')
    serializer_class = serializers.VLANGroupSerializer


#
# VLANs
#

class VLANListView(CustomFieldModelAPIView, generics.ListAPIView):
    """
    List VLANs (filterable)
    """
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.VLANSerializer
    filter_class = filters.VLANFilter


class VLANDetailView(CustomFieldModelAPIView, generics.RetrieveAPIView):
    """
    Retrieve a single VLAN
    """
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')\
        .prefetch_related('custom_field_values__field')
    serializer_class = serializers.VLANSerializer
