from rest_framework import generics

from ipam.models import VRF, Role, RIR, Aggregate, Prefix, IPAddress, VLAN
from ipam.filters import AggregateFilter, PrefixFilter, IPAddressFilter, VLANFilter, VRFFilter

from . import serializers


class VRFListView(generics.ListAPIView):
    """
    List all VRFs
    """
    queryset = VRF.objects.all()
    serializer_class = serializers.VRFSerializer
    filter_class = VRFFilter


class VRFDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single VRF
    """
    queryset = VRF.objects.all()
    serializer_class = serializers.VRFSerializer


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


class AggregateListView(generics.ListAPIView):
    """
    List aggregates (filterable)
    """
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer
    filter_class = AggregateFilter


class AggregateDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single aggregate
    """
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer


class PrefixListView(generics.ListAPIView):
    """
    List prefixes (filterable)
    """
    queryset = Prefix.objects.select_related('site', 'vrf', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer
    filter_class = PrefixFilter


class PrefixDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single prefix
    """
    queryset = Prefix.objects.select_related('site', 'vrf', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer


class IPAddressListView(generics.ListAPIView):
    """
    List IP addresses (filterable)
    """
    queryset = IPAddress.objects.select_related('vrf', 'interface__device', 'nat_inside')\
        .prefetch_related('nat_outside')
    serializer_class = serializers.IPAddressSerializer
    filter_class = IPAddressFilter


class IPAddressDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single IP address
    """
    queryset = IPAddress.objects.select_related('vrf', 'interface__device', 'nat_inside')\
        .prefetch_related('nat_outside')
    serializer_class = serializers.IPAddressSerializer


class VLANListView(generics.ListAPIView):
    """
    List VLANs (filterable)
    """
    queryset = VLAN.objects.select_related('site', 'role')
    serializer_class = serializers.VLANSerializer
    filter_class = VLANFilter


class VLANDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single VLAN
    """
    queryset = VLAN.objects.select_related('site', 'role')
    serializer_class = serializers.VLANSerializer
