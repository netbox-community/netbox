from django.contrib.auth.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.gfk_fields import GFKSerializerField
from netbox.api.serializers import (
    NestedGroupModelSerializer,
    NetBoxModelSerializer,
    OrganizationalModelSerializer,
    PrimaryModelSerializer,
)
from tenancy.choices import ContactPriorityChoices
from tenancy.models import Contact, ContactAssignment, ContactGroup, ContactRole

from .nested import NestedContactGroupSerializer

__all__ = (
    'ContactAssignmentSerializer',
    'ContactGroupSerializer',
    'ContactRoleSerializer',
    'ContactSerializer',
)


class ContactGroupSerializer(NestedGroupModelSerializer):
    parent = NestedContactGroupSerializer(required=False, allow_null=True, default=None)
    contact_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = ContactGroup
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 'contact_count', 'owner', 'comments', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'contact_count', '_depth')


class ContactRoleSerializer(OrganizationalModelSerializer):

    class Meta:
        model = ContactRole
        fields = [
            'id', 'url', 'display_url', 'display', 'name', 'slug', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')


class ContactSerializer(PrimaryModelSerializer):
    groups = SerializedPKRelatedField(
        queryset=ContactGroup.objects.all(),
        serializer=ContactGroupSerializer,
        required=False,
        many=True,
        nested=True
    )

    class Meta:
        model = Contact
        fields = [
            'id', 'url', 'display_url', 'display', 'groups', 'name', 'title', 'phone', 'email', 'address', 'link',
            'description', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class ContactAssignmentSerializer(NetBoxModelSerializer):
    object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    object = GFKSerializerField(read_only=True)
    contact = ContactSerializer(nested=True)
    role = ContactRoleSerializer(nested=True, required=False, allow_null=True)
    priority = ChoiceField(choices=ContactPriorityChoices, allow_blank=True, required=False, default=lambda: '')

    class Meta:
        model = ContactAssignment
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'contact', 'role', 'priority',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'contact', 'role', 'priority')
