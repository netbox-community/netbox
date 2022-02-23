from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django_pglocks import advisory_lock
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.views import APIView


from dcim.models import Site
from extras.api.views import CustomFieldModelViewSet
from ipam import filtersets
from ipam.models import *
from netbox.api.views import ModelViewSet, ObjectValidationMixin
from netbox.config import get_config
from utilities.constants import ADVISORY_LOCK_KEYS
from utilities.utils import count_related
from . import serializers


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


class PrefixViewSet(CustomFieldModelViewSet):
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


class IPRangeViewSet(CustomFieldModelViewSet):
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

    @swagger_auto_schema(responses={200: serializers.AvailablePrefixSerializer(many=True)})
    def get(self, request, pk):
        prefix = get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)
        available_prefixes = prefix.get_available_prefixes()

        serializer = serializers.AvailablePrefixSerializer(available_prefixes.iter_cidrs(), many=True, context={
            'request': request,
            'vrf': prefix.vrf,
        })

        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=serializers.PrefixLengthSerializer,
        responses={201: serializers.PrefixSerializer(many=True)}
    )
    @advisory_lock(ADVISORY_LOCK_KEYS['available-prefixes'])
    def post(self, request, pk):
        self.queryset = self.queryset.restrict(request.user, 'add')
        prefix = get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)
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
                    status=status.HTTP_409_CONFLICT
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


class AvailableIPAddressesView(ObjectValidationMixin, APIView):
    queryset = IPAddress.objects.all()

    def get_parent(self, request, pk):
        raise NotImplemented()

    @swagger_auto_schema(responses={200: serializers.AvailableIPSerializer(many=True)})
    def get(self, request, pk):
        parent = self.get_parent(request, pk)
        config = get_config()
        PAGINATE_COUNT = config.PAGINATE_COUNT
        MAX_PAGE_SIZE = config.MAX_PAGE_SIZE

        try:
            limit = int(request.query_params.get('limit', PAGINATE_COUNT))
        except ValueError:
            limit = PAGINATE_COUNT
        if MAX_PAGE_SIZE:
            limit = min(limit, MAX_PAGE_SIZE)

        # Calculate available IPs within the parent
        ip_list = []
        for index, ip in enumerate(parent.get_available_ips(), start=1):
            ip_list.append(ip)
            if index == limit:
                break
        serializer = serializers.AvailableIPSerializer(ip_list, many=True, context={
            'request': request,
            'parent': parent,
            'vrf': parent.vrf,
        })

        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=serializers.AvailableIPSerializer,
        responses={201: serializers.IPAddressSerializer(many=True)}
    )
    @advisory_lock(ADVISORY_LOCK_KEYS['available-ips'])
    def post(self, request, pk):
        self.queryset = self.queryset.restrict(request.user, 'add')
        parent = self.get_parent(request, pk)

        # Normalize to a list of objects
        requested_ips = request.data if isinstance(request.data, list) else [request.data]

        # Determine if the requested number of IPs is available
        available_ips = parent.get_available_ips()
        if available_ips.size < len(requested_ips):
            return Response(
                {
                    "detail": f"An insufficient number of IP addresses are available within {parent} "
                              f"({len(requested_ips)} requested, {len(available_ips)} available)"
                },
                status=status.HTTP_409_CONFLICT
            )

        # Assign addresses from the list of available IPs and copy VRF assignment from the parent
        available_ips = iter(available_ips)
        for requested_ip in requested_ips:
            mask_length = requested_ip.get('mask_length') or parent.mask_length
            requested_ip['address'] = f'{next(available_ips)}/{mask_length}'
            requested_ip['vrf'] = parent.vrf.pk if parent.vrf else None

        # Initialize the serializer with a list or a single object depending on what was requested
        context = {'request': request}
        if isinstance(request.data, list):
            serializer = serializers.IPAddressSerializer(data=requested_ips, many=True, context=context)
        else:
            serializer = serializers.IPAddressSerializer(data=requested_ips[0], context=context)

        # Create the new IP address(es)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    created = serializer.save()
                    self._validate_objects(created)
            except ObjectDoesNotExist:
                raise PermissionDenied()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrefixAvailableIPAddressesView(AvailableIPAddressesView):

    def get_parent(self, request, pk):
        return get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)


class IPRangeAvailableIPAddressesView(AvailableIPAddressesView):

    def get_parent(self, request, pk):
        return get_object_or_404(IPRange.objects.restrict(request.user), pk=pk)
