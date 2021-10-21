from django.contrib.auth.models import ContentType
from rest_framework import serializers

from netbox.api import ChoiceField, ContentTypeField
from netbox.api.serializers import NestedGroupModelSerializer, PrimaryModelSerializer
from tenancy.choices import ContactPriorityChoices
from tenancy.models import *
from .nested_serializers import *


#
# Tenants
#

class TenantGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenantgroup-detail')
    parent = NestedTenantGroupSerializer(required=False, allow_null=True)
    tenant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TenantGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'tenant_count', '_depth',
        ]


class TenantSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')
    group = NestedTenantGroupSerializer(required=False, allow_null=True)
    circuit_count = serializers.IntegerField(read_only=True)
    device_count = serializers.IntegerField(read_only=True)
    ipaddress_count = serializers.IntegerField(read_only=True)
    prefix_count = serializers.IntegerField(read_only=True)
    rack_count = serializers.IntegerField(read_only=True)
    site_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)
    vrf_count = serializers.IntegerField(read_only=True)
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'group', 'description', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'circuit_count', 'device_count', 'ipaddress_count', 'prefix_count', 'rack_count',
            'site_count', 'virtualmachine_count', 'vlan_count', 'vrf_count', 'cluster_count',
        ]


#
# Contacts
#

class ContactGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactgroup-detail')
    parent = NestedContactGroupSerializer(required=False, allow_null=True)
    contact_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'contact_count', '_depth',
        ]


class ContactRoleSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactrole-detail')

    class Meta:
        model = ContactRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class ContactSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contact-detail')
    group = NestedContactGroupSerializer(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'url', 'display', 'group', 'name', 'title', 'phone', 'email', 'address', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]


class ContactAssignmentSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactassignment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    contact = NestedContactSerializer()
    role = NestedContactRoleSerializer(required=False, allow_null=True)
    priority = ChoiceField(choices=ContactPriorityChoices, required=False)

    class Meta:
        model = ContactAssignment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'contact', 'role', 'priority', 'created',
            'last_updated',
        ]
