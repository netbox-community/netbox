from django.shortcuts import get_object_or_404

from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from dcim.models import Device
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

class AggregateViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Aggregate.objects.select_related('rir')
    serializer_class = serializers.AggregateSerializer
    write_serializer_class = serializers.WritableAggregateSerializer
    filter_class = filters.AggregateFilter


#
# Prefixes
#

class PrefixViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    serializer_class = serializers.PrefixSerializer
    write_serializer_class = serializers.WritablePrefixSerializer
    filter_class = filters.PrefixFilter


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

class ServiceViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, WritableSerializerMixin, GenericViewSet):
    queryset = Service.objects.select_related('device')
    serializer_class = serializers.ServiceSerializer


class DeviceServiceViewSet(CreateModelMixin, ListModelMixin, WritableSerializerMixin, GenericViewSet):
    serializer_class = serializers.DeviceServiceSerializer

    def get_queryset(self):
        device = get_object_or_404(Device, pk=self.kwargs['pk'])
        return Service.objects.filter(device=device).select_related('device')
