from django.db.models import Count

from extras.api.views import CustomFieldModelViewSet
from tenancy import filters
from tenancy.models import Tenant, TenantGroup
from utilities.api import FieldChoicesViewSet, ModelViewSet
from . import serializers


#
# Field choices
#

class TenancyFieldChoicesViewSet(FieldChoicesViewSet):
    fields = ()


#
# Tenant Groups
#

class TenantGroupViewSet(ModelViewSet):
    queryset = TenantGroup.objects.annotate(
        tenant_count=Count('tenants')
    )
    serializer_class = serializers.TenantGroupSerializer
    filterset_class = filters.TenantGroupFilter


#
# Tenants
#

class TenantViewSet(CustomFieldModelViewSet):
    queryset = Tenant.objects.select_related('group').prefetch_related('tags')
    serializer_class = serializers.TenantSerializer
    filterset_class = filters.TenantFilter
