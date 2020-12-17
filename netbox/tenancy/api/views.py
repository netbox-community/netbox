from rest_framework.routers import APIRootView

from circuits.models import Circuit
from dcim.models import Device, Rack, Site
from extras.api.views import CustomFieldModelViewSet
from ipam.models import IPAddress, Prefix, VLAN, VRF
from netbox.api.views import ModelViewSet
from tenancy import filters
from tenancy.models import Tenant, TenantGroup
from utilities.utils import get_subquery
from virtualization.models import VirtualMachine
from . import serializers


class TenancyRootView(APIRootView):
    """
    Tenancy API root view
    """
    def get_view_name(self):
        return 'Tenancy'


#
# Tenant Groups
#

class TenantGroupViewSet(ModelViewSet):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    serializer_class = serializers.TenantGroupSerializer
    filterset_class = filters.TenantGroupFilterSet


#
# Tenants
#

class TenantViewSet(CustomFieldModelViewSet):
    queryset = Tenant.objects.prefetch_related(
        'group', 'tags'
    ).annotate(
        circuit_count=get_subquery(Circuit, 'tenant'),
        device_count=get_subquery(Device, 'tenant'),
        ipaddress_count=get_subquery(IPAddress, 'tenant'),
        prefix_count=get_subquery(Prefix, 'tenant'),
        rack_count=get_subquery(Rack, 'tenant'),
        site_count=get_subquery(Site, 'tenant'),
        virtualmachine_count=get_subquery(VirtualMachine, 'tenant'),
        vlan_count=get_subquery(VLAN, 'tenant'),
        vrf_count=get_subquery(VRF, 'tenant')
    )
    serializer_class = serializers.TenantSerializer
    filterset_class = filters.TenantFilterSet
