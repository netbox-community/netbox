from django.contrib.auth.models import ContentType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.choices import ContactPriorityChoices
from tenancy.models import *
from utilities.api import get_serializer_for_model
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


class TenantSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:tenant-detail')
    group = NestedTenantGroupSerializer(required=False, allow_null=True)

    # Related object counts
    circuit_count = RelatedObjectCountField('circuits.circuit', 'tenant')
    device_count = RelatedObjectCountField('dcim.device', 'tenant')
    rack_count = RelatedObjectCountField('dcim.rack', 'tenant')
    site_count = RelatedObjectCountField('dcim.site', 'tenant')
    ipaddress_count = RelatedObjectCountField('ipam.ipaddress', 'tenant')
    prefix_count = RelatedObjectCountField('ipam.prefix', 'tenant')
    vlan_count = RelatedObjectCountField('ipam.vlan', 'tenant')
    vrf_count = RelatedObjectCountField('ipam.vrf', 'tenant')
    virtualmachine_count = RelatedObjectCountField('virtualization.virtualmachine', 'tenant')
    cluster_count = RelatedObjectCountField('virtualization.cluster', 'tenant')

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
    parent = NestedContactGroupSerializer(required=False, allow_null=True, default=None)
    contact_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'contact_count', '_depth',
        ]


class ContactRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactrole-detail')

    class Meta:
        model = ContactRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class ContactSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contact-detail')
    group = NestedContactGroupSerializer(required=False, allow_null=True, default=None)

    class Meta:
        model = Contact
        fields = [
            'id', 'url', 'display', 'group', 'name', 'title', 'phone', 'email', 'address', 'link', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class ContactAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='tenancy-api:contactassignment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    object = serializers.SerializerMethodField(read_only=True)
    contact = NestedContactSerializer()
    role = NestedContactRoleSerializer(required=False, allow_null=True)
    priority = ChoiceField(choices=ContactPriorityChoices, allow_blank=True, required=False, default=lambda: '')

    class Meta:
        model = ContactAssignment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'object', 'contact', 'role', 'priority', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.content_type.model_class(), prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(instance.object, context=context).data
