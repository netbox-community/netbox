from __future__ import unicode_literals

from rest_framework.viewsets import ModelViewSet

from extras.api.views import CustomFieldModelViewSet
from tenancy import filters
from tenancy.models import Tenant, TenantGroup
from utilities.api import FieldChoicesViewSet, WritableSerializerMixin
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

class TenantViewSet(WritableSerializerMixin, CustomFieldModelViewSet):
    queryset = Tenant.objects.select_related('group')
    serializer_class = serializers.TenantSerializer
    write_serializer_class = serializers.WritableTenantSerializer
    filter_class = filters.TenantFilter
