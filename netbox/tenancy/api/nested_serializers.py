import warnings

from netbox.api.serializers import WritableNestedSerializer
from serializers_.nested import NestedContactGroupSerializer, NestedTenantGroupSerializer
from tenancy.models import *

__all__ = [
    'NestedContactSerializer',
    'NestedContactAssignmentSerializer',
    'NestedContactGroupSerializer',
    'NestedContactRoleSerializer',
    'NestedTenantGroupSerializer',
    'NestedTenantSerializer',
]

# TODO: Remove in v4.2
warnings.warn(
    "Dedicated nested serializers will be removed in NetBox v4.2. Use Serializer(nested=True) instead.",
    DeprecationWarning
)


#
# Tenants
#

class NestedTenantSerializer(WritableNestedSerializer):

    class Meta:
        model = Tenant
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug']


#
# Contacts
#

class NestedContactRoleSerializer(WritableNestedSerializer):

    class Meta:
        model = ContactRole
        fields = ['id', 'url', 'display_url', 'display', 'name', 'slug']


class NestedContactSerializer(WritableNestedSerializer):

    class Meta:
        model = Contact
        fields = ['id', 'url', 'display_url', 'display', 'name']


class NestedContactAssignmentSerializer(WritableNestedSerializer):
    contact = NestedContactSerializer()
    role = NestedContactRoleSerializer

    class Meta:
        model = ContactAssignment
        fields = ['id', 'url', 'display', 'contact', 'role', 'priority']
