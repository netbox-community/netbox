from rest_framework.viewsets import ModelViewSet

from tenancy.models import Tenant, TenantGroup
from tenancy.filters import TenantFilter

from extras.api.views import CustomFieldModelViewSet
from utilities.api import WritableSerializerMixin
from . import serializers


#
# Tenant Groups
#

class TenantGroupViewSet(ModelViewSet):
    queryset = TenantGroup.objects.all()
    serializer_class = serializers.TenantGroupSerializer


#
# Tenants
#

class TenantViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Tenant.objects.select_related('group')
    serializer_class = serializers.TenantSerializer
    write_serializer_class = serializers.WritableTenantSerializer
    filter_class = TenantFilter
