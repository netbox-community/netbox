from rest_framework import generics

from tenancy.models import Tenant, TenantGroup
from tenancy.filters import TenantFilter

from . import serializers


class TenantGroupListView(generics.ListAPIView):
    """
    List all tenant groups
    """
    queryset = TenantGroup.objects.all()
    serializer_class = serializers.TenantGroupSerializer


class TenantGroupDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single circuit type
    """
    queryset = TenantGroup.objects.all()
    serializer_class = serializers.TenantGroupSerializer


class TenantListView(generics.ListAPIView):
    """
    List tenants (filterable)
    """
    queryset = Tenant.objects.select_related('group')
    serializer_class = serializers.TenantSerializer
    filter_class = TenantFilter


class TenantDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single tenant
    """
    queryset = Tenant.objects.select_related('group')
    serializer_class = serializers.TenantSerializer
