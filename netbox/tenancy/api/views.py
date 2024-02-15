from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet, MPTTLockedMixin
from tenancy import filtersets
from tenancy.models import *
from . import serializers


class TenancyRootView(APIRootView):
    """
    Tenancy API root view
    """
    def get_view_name(self):
        return 'Tenancy'


#
# Tenants
#

class TenantGroupViewSet(MPTTLockedMixin, NetBoxModelViewSet):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    serializer_class = serializers.TenantGroupSerializer
    filterset_class = filtersets.TenantGroupFilterSet


class TenantViewSet(NetBoxModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = serializers.TenantSerializer
    filterset_class = filtersets.TenantFilterSet


#
# Contacts
#

class ContactGroupViewSet(MPTTLockedMixin, NetBoxModelViewSet):
    queryset = ContactGroup.objects.add_related_count(
        ContactGroup.objects.all(),
        Contact,
        'group',
        'contact_count',
        cumulative=True
    )
    serializer_class = serializers.ContactGroupSerializer
    filterset_class = filtersets.ContactGroupFilterSet


class ContactRoleViewSet(NetBoxModelViewSet):
    queryset = ContactRole.objects.all()
    serializer_class = serializers.ContactRoleSerializer
    filterset_class = filtersets.ContactRoleFilterSet


class ContactViewSet(NetBoxModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filterset_class = filtersets.ContactFilterSet


class ContactAssignmentViewSet(NetBoxModelViewSet):
    queryset = ContactAssignment.objects.all()
    serializer_class = serializers.ContactAssignmentSerializer
    filterset_class = filtersets.ContactAssignmentFilterSet
