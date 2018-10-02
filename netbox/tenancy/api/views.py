from __future__ import unicode_literals

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
    queryset = TenantGroup.objects.all()
    serializer_class = serializers.TenantGroupSerializer
    filter_class = filters.TenantGroupFilter


#
# Tenants
#

class TenantViewSet(CustomFieldModelViewSet):
    queryset = Tenant.objects.select_related('group').prefetch_related('tags')
    serializer_class = serializers.TenantSerializer
    filter_class = filters.TenantFilter
