from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_pglocks import advisory_lock
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ipam.models import *
from netbox.config import get_config
from utilities.constants import ADVISORY_LOCK_KEYS
from . import serializers


class AvailableIPsMixin:
    parent_model = Prefix

    @swagger_auto_schema(method='get', responses={200: serializers.AvailableIPSerializer(many=True)})
    @swagger_auto_schema(method='post', responses={201: serializers.AvailableIPSerializer(many=True)},
                         request_body=serializers.AvailableIPSerializer(many=True))
    @action(detail=True, url_path='available-ips', methods=['get', 'post'], queryset=IPAddress.objects.all())
    @advisory_lock(ADVISORY_LOCK_KEYS['available-ips'])
    def available_ips(self, request, pk=None):
        """
        A convenience method for returning available IP addresses within a Prefix or IPRange. By default, the number of
        IPs returned will be equivalent to PAGINATE_COUNT. An arbitrary limit (up to MAX_PAGE_SIZE, if set) may be
        passed, however results will not be paginated.

        The advisory lock decorator uses a PostgreSQL advisory lock to prevent this API from being
        invoked in parallel, which results in a race condition where multiple insertions can occur.
        """
        parent = get_object_or_404(self.parent_model.objects.restrict(request.user), pk=pk)

        # Create the next available IP
        if request.method == 'POST':

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
                    status=status.HTTP_204_NO_CONTENT
                )

            # Assign addresses from the list of available IPs and copy VRF assignment from the parent
            available_ips = iter(available_ips)
            for requested_ip in requested_ips:
                requested_ip['address'] = f'{next(available_ips)}/{parent.mask_length}'
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

        # Determine the maximum number of IPs to return
        else:
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
