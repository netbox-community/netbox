from rest_framework.viewsets import ModelViewSet

from tenancy.models import Tenant, TenantGroup
from tenancy.filters import TenantFilter

from extras.api.views import CustomFieldModelViewSet
from . import serializers


#
# Tenant Groups
#

class TenantGroupViewSet(ModelViewSet):
    """
    List and retrieve tenant groups
    """
    queryset = TenantGroup.objects.all()
    serializer_class = serializers.TenantGroupSerializer


#
# Tenants
#

class TenantViewSet(CustomFieldModelViewSet):
    """
    List and retrieve tenants
    """
    queryset = Tenant.objects.select_related('group')
    serializer_class = serializers.TenantSerializer
    filter_class = TenantFilter
