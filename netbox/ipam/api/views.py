from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django_pglocks import advisory_lock
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView


from dcim.models import Site
from extras.api.views import CustomFieldModelViewSet
from ipam import filtersets
from ipam.models import *
from netbox.api.views import ModelViewSet, ObjectValidationMixin
from utilities.constants import ADVISORY_LOCK_KEYS
from utilities.utils import count_related
from . import mixins, serializers


class IPAMRootView(APIRootView):
    """
    IPAM API root view
    """
    def get_view_name(self):
        return 'IPAM'


#
# Viewsets
#

class ASNViewSet(CustomFieldModelViewSet):
    queryset = ASN.objects.prefetch_related('tenant', 'rir').annotate(site_count=count_related(Site, 'asns'))
    serializer_class = serializers.ASNSerializer
    filterset_class = filtersets.ASNFilterSet


class VRFViewSet(CustomFieldModelViewSet):
    queryset = VRF.objects.prefetch_related('tenant').prefetch_related(
        'import_targets', 'export_targets', 'tags'
    ).annotate(
        ipaddress_count=count_related(IPAddress, 'vrf'),
        prefix_count=count_related(Prefix, 'vrf')
    )
    serializer_class = serializers.VRFSerializer
    filterset_class = filtersets.VRFFilterSet


class RouteTargetViewSet(CustomFieldModelViewSet):
    queryset = RouteTarget.objects.prefetch_related('tenant').prefetch_related('tags')
    serializer_class = serializers.RouteTargetSerializer
    filterset_class = filtersets.RouteTargetFilterSet


class RIRViewSet(CustomFieldModelViewSet):
    queryset = RIR.objects.annotate(
        aggregate_count=count_related(Aggregate, 'rir')
    ).prefetch_related('tags')
    serializer_class = serializers.RIRSerializer
    filterset_class = filtersets.RIRFilterSet


class AggregateViewSet(CustomFieldModelViewSet):
    queryset = Aggregate.objects.prefetch_related('rir').prefetch_related('tags')
    serializer_class = serializers.AggregateSerializer
    filterset_class = filtersets.AggregateFilterSet


class RoleViewSet(CustomFieldModelViewSet):
    queryset = Role.objects.annotate(
        prefix_count=count_related(Prefix, 'role'),
        vlan_count=count_related(VLAN, 'role')
    ).prefetch_related('tags')
    serializer_class = serializers.RoleSerializer
    filterset_class = filtersets.RoleFilterSet


class PrefixViewSet(mixins.AvailableIPsMixin, CustomFieldModelViewSet):
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


class IPRangeViewSet(mixins.AvailableIPsMixin, CustomFieldModelViewSet):
    queryset = IPRange.objects.prefetch_related('vrf', 'role', 'tenant', 'tags')
    serializer_class = serializers.IPRangeSerializer
    filterset_class = filtersets.IPRangeFilterSet

    parent_model = IPRange  # AvailableIPsMixin


class IPAddressViewSet(CustomFieldModelViewSet):
    queryset = IPAddress.objects.prefetch_related(
        'vrf__tenant', 'tenant', 'nat_inside', 'nat_outside', 'tags', 'assigned_object'
    )
    serializer_class = serializers.IPAddressSerializer
    filterset_class = filtersets.IPAddressFilterSet


class FHRPGroupViewSet(CustomFieldModelViewSet):
    queryset = FHRPGroup.objects.prefetch_related('ip_addresses', 'tags')
    serializer_class = serializers.FHRPGroupSerializer
    filterset_class = filtersets.FHRPGroupFilterSet
    brief_prefetch_fields = ('ip_addresses',)


class FHRPGroupAssignmentViewSet(CustomFieldModelViewSet):
    queryset = FHRPGroupAssignment.objects.prefetch_related('group', 'interface')
    serializer_class = serializers.FHRPGroupAssignmentSerializer
    filterset_class = filtersets.FHRPGroupAssignmentFilterSet


class VLANGroupViewSet(CustomFieldModelViewSet):
    queryset = VLANGroup.objects.annotate(
        vlan_count=count_related(VLAN, 'group')
    ).prefetch_related('tags')
    serializer_class = serializers.VLANGroupSerializer
    filterset_class = filtersets.VLANGroupFilterSet


class VLANViewSet(CustomFieldModelViewSet):
    queryset = VLAN.objects.prefetch_related(
        'site', 'group', 'tenant', 'role', 'tags'
    ).annotate(
        prefix_count=count_related(Prefix, 'vlan')
    )
    serializer_class = serializers.VLANSerializer
    filterset_class = filtersets.VLANFilterSet


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.prefetch_related(
        'device', 'virtual_machine', 'tags', 'ipaddresses'
    )
    serializer_class = serializers.ServiceSerializer
    filterset_class = filtersets.ServiceFilterSet


#
# Views
#

class AvailablePrefixesView(ObjectValidationMixin, APIView):
    queryset = Prefix.objects.all()

    def get(self, request, pk):
        prefix = get_object_or_404(self.queryset, pk=pk)
        available_prefixes = prefix.get_available_prefixes()

        serializer = serializers.AvailablePrefixSerializer(available_prefixes.iter_cidrs(), many=True, context={
            'request': request,
            'vrf': prefix.vrf,
        })

        return Response(serializer.data)

    @advisory_lock(ADVISORY_LOCK_KEYS['available-prefixes'])
    def post(self, request, pk):
        prefix = get_object_or_404(self.queryset, pk=pk)
        available_prefixes = prefix.get_available_prefixes()

        # Validate Requested Prefixes' length
        serializer = serializers.PrefixLengthSerializer(
            data=request.data if isinstance(request.data, list) else [request.data],
            many=True,
            context={
                'request': request,
                'prefix': prefix,
            }
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_prefixes = serializer.validated_data
        # Allocate prefixes to the requested objects based on availability within the parent
        for i, requested_prefix in enumerate(requested_prefixes):

            # Find the first available prefix equal to or larger than the requested size
            for available_prefix in available_prefixes.iter_cidrs():
                if requested_prefix['prefix_length'] >= available_prefix.prefixlen:
                    allocated_prefix = '{}/{}'.format(available_prefix.network, requested_prefix['prefix_length'])
                    requested_prefix['prefix'] = allocated_prefix
                    requested_prefix['vrf'] = prefix.vrf.pk if prefix.vrf else None
                    break
            else:
                return Response(
                    {
                        "detail": "Insufficient space is available to accommodate the requested prefix size(s)"
                    },
                    status=status.HTTP_204_NO_CONTENT
                )

            # Remove the allocated prefix from the list of available prefixes
            available_prefixes.remove(allocated_prefix)

        # Initialize the serializer with a list or a single object depending on what was requested
        context = {'request': request}
        if isinstance(request.data, list):
            serializer = serializers.PrefixSerializer(data=requested_prefixes, many=True, context=context)
        else:
            serializer = serializers.PrefixSerializer(data=requested_prefixes[0], context=context)

        # Create the new Prefix(es)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    created = serializer.save()
                    self._validate_objects(created)
            except ObjectDoesNotExist:
                raise PermissionDenied()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
