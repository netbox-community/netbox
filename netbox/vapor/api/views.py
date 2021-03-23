
from rest_framework.response import Response
from rest_framework.decorators import action

from dcim.api.views import PathEndpointMixin
from dcim.models import Interface
from extras.api.views import CustomFieldModelViewSet
from tenancy.models import Tenant as Customer
from netbox.api.views import ModelViewSet
from vapor import filters

from . import serializers


class CustomerViewSet(CustomFieldModelViewSet):
    queryset = Customer.objects.prefetch_related(
        'group', 'tags', 'devices'
    )
    serializer_class = serializers.CustomerSerializer
    filterset_class = filters.CustomerFilter


class InterfaceViewSet(PathEndpointMixin, ModelViewSet):
    queryset = Interface.objects.prefetch_related(
        'device', '_path__destination', 'cable', '_cable_peer', 'ip_addresses', 'tags'
    )
    serializer_class = serializers.InterfaceSerializer
    filterset_class = filters.InterfaceFilter
    brief_prefetch_fields = ['device']
