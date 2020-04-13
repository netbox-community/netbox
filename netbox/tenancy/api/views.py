from circuits.models import Circuit
from dcim.models import Device, Rack, Site
from extras.api.views import CustomFieldModelViewSet
from ipam.models import IPAddress, Prefix, VLAN, VRF
from tenancy import filters
from tenancy.models import Tenant, TenantGroup
from utilities.api import ModelViewSet
from utilities.utils import get_subquery
from virtualization.models import VirtualMachine
from . import serializers


#
# Tenant Groups
#

class TenantGroupViewSet(ModelViewSet):
    queryset = TenantGroup.objects.annotate(
        tenant_count=get_subquery(Tenant, 'group')
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
