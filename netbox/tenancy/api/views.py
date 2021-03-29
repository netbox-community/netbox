from rest_framework.routers import APIRootView

from circuits.models import Circuit
from dcim.models import Device, Rack, Site
from extras.api.views import CustomFieldModelViewSet
from ipam.models import IPAddress, Prefix, VLAN, VRF
from tenancy import filters
from tenancy.models import Tenant, TenantGroup
from utilities.utils import count_related
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

class TenantGroupViewSet(CustomFieldModelViewSet):
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
        circuit_count=count_related(Circuit, 'tenant'),
        device_count=count_related(Device, 'tenant'),
        ipaddress_count=count_related(IPAddress, 'tenant'),
        prefix_count=count_related(Prefix, 'tenant'),
        rack_count=count_related(Rack, 'tenant'),
        site_count=count_related(Site, 'tenant'),
        virtualmachine_count=count_related(VirtualMachine, 'tenant'),
        vlan_count=count_related(VLAN, 'tenant'),
        vrf_count=count_related(VRF, 'tenant')
    )
    serializer_class = serializers.TenantSerializer
    filterset_class = filters.TenantFilterSet
