from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from extras.api.views import CustomFieldModelViewSet
from ipam import filters
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from utilities.api import FieldChoicesViewSet, ModelViewSet
from . import serializers


#
# Field choices
#

class IPAMFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Aggregate, ['family']),
        (Prefix, ['family', 'status']),
        (IPAddress, ['family', 'status', 'role']),
        (VLAN, ['status']),
        (Service, ['protocol']),
    )


#
# VRFs
#

class VRFViewSet(CustomFieldModelViewSet):
    queryset = VRF.objects.select_related('tenant').prefetch_related('tags')
    serializer_class = serializers.VRFSerializer
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

class AggregateViewSet(CustomFieldModelViewSet):
    queryset = Aggregate.objects.select_related('rir').prefetch_related('tags')
    serializer_class = serializers.AggregateSerializer
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

class PrefixViewSet(CustomFieldModelViewSet):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role').prefetch_related('tags')
    serializer_class = serializers.PrefixSerializer
    filter_class = filters.PrefixFilter

    @action(detail=True, url_path='available-prefixes', methods=['get', 'post'])
    def available_prefixes(self, request, pk=None):
        """
        A convenience method for returning available child prefixes within a parent.
        """
        prefix = get_object_or_404(Prefix, pk=pk)
        available_prefixes = prefix.get_available_prefixes()

        if request.method == 'POST':

            # Permissions check
            if not request.user.has_perm('ipam.add_prefix'):
                raise PermissionDenied()

            # Normalize to a list of objects
            requested_prefixes = request.data if isinstance(request.data, list) else [request.data]

            # Allocate prefixes to the requested objects based on availability within the parent
            for i, requested_prefix in enumerate(requested_prefixes):

                # Validate requested prefix size
                error_msg = None
                if 'prefix_length' not in requested_prefix:
                    error_msg = "Item {}: prefix_length field missing".format(i)
                elif not isinstance(requested_prefix['prefix_length'], int):
                    error_msg = "Item {}: Invalid prefix length ({})".format(
                        i, requested_prefix['prefix_length']
                    )
                elif prefix.family == 4 and requested_prefix['prefix_length'] > 32:
                    error_msg = "Item {}: Invalid prefix length ({}) for IPv4".format(
                        i, requested_prefix['prefix_length']
                    )
                elif prefix.family == 6 and requested_prefix['prefix_length'] > 128:
                    error_msg = "Item {}: Invalid prefix length ({}) for IPv6".format(
                        i, requested_prefix['prefix_length']
                    )
                if error_msg:
                    return Response(
                        {
                            "detail": error_msg
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

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
                        status=status.HTTP_400_BAD_REQUEST
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
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:

            serializer = serializers.AvailablePrefixSerializer(available_prefixes.iter_cidrs(), many=True, context={
                'request': request,
                'vrf': prefix.vrf,
            })

            return Response(serializer.data)

    @action(detail=True, url_path='available-ips', methods=['get', 'post'])
    def available_ips(self, request, pk=None):
        """
        A convenience method for returning available IP addresses within a prefix. By default, the number of IPs
        returned will be equivalent to PAGINATE_COUNT. An arbitrary limit (up to MAX_PAGE_SIZE, if set) may be passed,
        however results will not be paginated.
        """
        prefix = get_object_or_404(Prefix, pk=pk)

        # Create the next available IP within the prefix
        if request.method == 'POST':

            # Permissions check
            if not request.user.has_perm('ipam.add_ipaddress'):
                raise PermissionDenied()

            # Normalize to a list of objects
            requested_ips = request.data if isinstance(request.data, list) else [request.data]

            # Determine if the requested number of IPs is available
            available_ips = prefix.get_available_ips()
            if available_ips.size < len(requested_ips):
                return Response(
                    {
                        "detail": "An insufficient number of IP addresses are available within the prefix {} ({} "
                                  "requested, {} available)".format(prefix, len(requested_ips), len(available_ips))
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Assign addresses from the list of available IPs and copy VRF assignment from the parent prefix
            available_ips = iter(available_ips)
            prefix_length = prefix.prefix.prefixlen
            for requested_ip in requested_ips:
                requested_ip['address'] = '{}/{}'.format(next(available_ips), prefix_length)
                requested_ip['vrf'] = prefix.vrf.pk if prefix.vrf else None

            # Initialize the serializer with a list or a single object depending on what was requested
            context = {'request': request}
            if isinstance(request.data, list):
                serializer = serializers.IPAddressSerializer(data=requested_ips, many=True, context=context)
            else:
                serializer = serializers.IPAddressSerializer(data=requested_ips[0], context=context)

            # Create the new IP address(es)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Determine the maximum number of IPs to return
        else:
            try:
                limit = int(request.query_params.get('limit', settings.PAGINATE_COUNT))
            except ValueError:
                limit = settings.PAGINATE_COUNT
            if settings.MAX_PAGE_SIZE:
                limit = min(limit, settings.MAX_PAGE_SIZE)

            # Calculate available IPs within the prefix
            ip_list = []
            for index, ip in enumerate(prefix.get_available_ips(), start=1):
                ip_list.append(ip)
                if index == limit:
                    break
            serializer = serializers.AvailableIPSerializer(ip_list, many=True, context={
                'request': request,
                'prefix': prefix.prefix,
                'vrf': prefix.vrf,
            })

            return Response(serializer.data)


#
# IP addresses
#

class IPAddressViewSet(CustomFieldModelViewSet):
    queryset = IPAddress.objects.select_related(
        'vrf__tenant', 'tenant', 'nat_inside', 'interface__device__device_type', 'interface__virtual_machine'
    ).prefetch_related(
        'nat_outside', 'tags',
    )
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
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role').prefetch_related('tags')
    serializer_class = serializers.VLANSerializer
    filter_class = filters.VLANFilter


#
# Services
#

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.select_related('device').prefetch_related('tags')
    serializer_class = serializers.ServiceSerializer
    filter_class = filters.ServiceFilter
