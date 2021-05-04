from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from dcim.api.nested_serializers import (
    NestedDeviceSerializer, NestedDeviceRoleSerializer, NestedDeviceTypeSerializer, NestedPlatformSerializer,
    NestedRackSerializer, NestedRegionSerializer, NestedSiteSerializer, NestedSiteGroupSerializer,
)
from dcim.models import Device, DeviceRole, DeviceType, Platform, Rack, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from netbox.api import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.exceptions import SerializerNotFound
from netbox.api.serializers import BaseModelSerializer, ValidatedModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer, NestedTenantGroupSerializer
from tenancy.models import Tenant, TenantGroup
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import get_serializer_for_model
from virtualization.api.nested_serializers import NestedClusterGroupSerializer, NestedClusterSerializer
from virtualization.models import Cluster, ClusterGroup
from .nested_serializers import *

__all__ = (
    'ConfigContextSerializer',
    'ContentTypeSerializer',
    'CustomFieldSerializer',
    'CustomLinkSerializer',
    'ExportTemplateSerializer',
    'ImageAttachmentSerializer',
    'JobResultSerializer',
    'ObjectChangeSerializer',
    'ReportDetailSerializer',
    'ReportSerializer',
    'ScriptDetailSerializer',
    'ScriptInputSerializer',
    'ScriptLogMessageSerializer',
    'ScriptOutputSerializer',
    'ScriptSerializer',
    'TagSerializer',
    'WebhookSerializer',
)


#
# Webhooks
#

class WebhookSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:webhook-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('webhooks').get_query()),
        many=True
    )

    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'type_create', 'type_update', 'type_delete', 'payload_url',
            'enabled', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
            'ssl_verification', 'ca_file_path',
        ]


#
# Custom fields
#

class CustomFieldSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfield-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('custom_fields').get_query()),
        many=True
    )
    type = ChoiceField(choices=CustomFieldTypeChoices)
    filter_logic = ChoiceField(choices=CustomFieldFilterLogicChoices, required=False)

    class Meta:
        model = CustomField
        fields = [
            'id', 'url', 'display', 'content_types', 'type', 'name', 'label', 'description', 'required', 'filter_logic',
            'default', 'weight', 'validation_minimum', 'validation_maximum', 'validation_regex', 'choices',
        ]


#
# Custom links
#

class CustomLinkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('custom_links').get_query())
    )

    class Meta:
        model = CustomLink
        fields = [
            'id', 'url', 'display', 'content_type', 'name', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window',
        ]


#
# Export templates
#

class ExportTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:exporttemplate-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('export_templates').get_query()),
    )

    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'url', 'display', 'content_type', 'name', 'description', 'template_code', 'mime_type',
            'file_extension', 'as_attachment',
        ]


#
# Tags
#

class TagSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')
    tagged_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'url', 'display', 'name', 'slug', 'color', 'description', 'tagged_items']


#
# Image attachments
#

class ImageAttachmentSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:imageattachment-detail')
    content_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImageAttachment
        fields = [
            'id', 'url', 'display', 'content_type', 'object_id', 'parent', 'name', 'image', 'image_height',
            'image_width', 'created',
        ]

    def validate(self, data):

        # Validate that the parent object exists
        try:
            data['content_type'].get_object_for_this_type(id=data['object_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid parent object: {} ID {}".format(data['content_type'], data['object_id'])
            )

        # Enforce model validation
        super().validate(data)

        return data

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_parent(self, obj):

        # Static mapping of models to their nested serializers
        if isinstance(obj.parent, Device):
            serializer = NestedDeviceSerializer
        elif isinstance(obj.parent, Rack):
            serializer = NestedRackSerializer
        elif isinstance(obj.parent, Site):
            serializer = NestedSiteSerializer
        else:
            raise Exception("Unexpected type of parent object for ImageAttachment")

        return serializer(obj.parent, context={'request': self.context['request']}).data


#
# Journal entries
#

class JournalEntrySerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:journalentry-detail')
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)
    kind = ChoiceField(
        choices=JournalEntryKindChoices,
        required=False
    )

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'url', 'display', 'assigned_object_type', 'assigned_object_id', 'assigned_object', 'created',
            'created_by', 'kind', 'comments',
        ]

    def validate(self, data):

        # Validate that the parent object exists
        if 'assigned_object_type' in data and 'assigned_object_id' in data:
            try:
                data['assigned_object_type'].get_object_for_this_type(id=data['assigned_object_id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid assigned_object: {data['assigned_object_type']} ID {data['assigned_object_id']}"
                )

        # Enforce model validation
        super().validate(data)

        return data

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_assigned_object(self, instance):
        serializer = get_serializer_for_model(instance.assigned_object_type.model_class(), prefix='Nested')
        context = {'request': self.context['request']}
        return serializer(instance.assigned_object, context=context).data


#
# Config contexts
#

class ConfigContextSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configcontext-detail')
    regions = SerializedPKRelatedField(
        queryset=Region.objects.all(),
        serializer=NestedRegionSerializer,
        required=False,
        many=True
    )
    site_groups = SerializedPKRelatedField(
        queryset=SiteGroup.objects.all(),
        serializer=NestedSiteGroupSerializer,
        required=False,
        many=True
    )
    sites = SerializedPKRelatedField(
        queryset=Site.objects.all(),
        serializer=NestedSiteSerializer,
        required=False,
        many=True
    )
    device_types = SerializedPKRelatedField(
        queryset=DeviceType.objects.all(),
        serializer=NestedDeviceTypeSerializer,
        required=False,
        many=True
    )
    roles = SerializedPKRelatedField(
        queryset=DeviceRole.objects.all(),
        serializer=NestedDeviceRoleSerializer,
        required=False,
        many=True
    )
    platforms = SerializedPKRelatedField(
        queryset=Platform.objects.all(),
        serializer=NestedPlatformSerializer,
        required=False,
        many=True
    )
    cluster_groups = SerializedPKRelatedField(
        queryset=ClusterGroup.objects.all(),
        serializer=NestedClusterGroupSerializer,
        required=False,
        many=True
    )
    clusters = SerializedPKRelatedField(
        queryset=Cluster.objects.all(),
        serializer=NestedClusterSerializer,
        required=False,
        many=True
    )
    tenant_groups = SerializedPKRelatedField(
        queryset=TenantGroup.objects.all(),
        serializer=NestedTenantGroupSerializer,
        required=False,
        many=True
    )
    tenants = SerializedPKRelatedField(
        queryset=Tenant.objects.all(),
        serializer=NestedTenantSerializer,
        required=False,
        many=True
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='slug',
        required=False,
        many=True
    )

    class Meta:
        model = ConfigContext
        fields = [
            'id', 'url', 'display', 'name', 'weight', 'description', 'is_active', 'regions', 'site_groups', 'sites',
            'device_types', 'roles', 'platforms', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'tags',
            'data', 'created', 'last_updated',
        ]


#
# Job Results
#

class JobResultSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:jobresult-detail')
    user = NestedUserSerializer(
        read_only=True
    )
    status = ChoiceField(choices=JobResultStatusChoices, read_only=True)
    obj_type = ContentTypeField(
        read_only=True
    )

    class Meta:
        model = JobResult
        fields = [
            'id', 'url', 'display', 'created', 'completed', 'name', 'obj_type', 'status', 'user', 'data', 'job_id',
        ]


#
# Reports
#

class ReportSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:report-detail',
        lookup_field='full_name',
        lookup_url_kwarg='pk'
    )
    id = serializers.CharField(read_only=True, source="full_name")
    module = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255, required=False)
    test_methods = serializers.ListField(child=serializers.CharField(max_length=255))
    result = NestedJobResultSerializer()


class ReportDetailSerializer(ReportSerializer):
    result = JobResultSerializer()


#
# Scripts
#

class ScriptSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:script-detail',
        lookup_field='full_name',
        lookup_url_kwarg='pk'
    )
    id = serializers.CharField(read_only=True, source="full_name")
    module = serializers.CharField(max_length=255)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    vars = serializers.SerializerMethodField(read_only=True)
    result = NestedJobResultSerializer()

    def get_vars(self, instance):
        return {
            k: v.__class__.__name__ for k, v in instance._get_vars().items()
        }


class ScriptDetailSerializer(ScriptSerializer):
    result = JobResultSerializer()


class ScriptInputSerializer(serializers.Serializer):
    data = serializers.JSONField()
    commit = serializers.BooleanField()


class ScriptLogMessageSerializer(serializers.Serializer):
    status = serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    def get_status(self, instance):
        return instance[0]

    def get_message(self, instance):
        return instance[1]


class ScriptOutputSerializer(serializers.Serializer):
    log = ScriptLogMessageSerializer(many=True, read_only=True)
    output = serializers.CharField(read_only=True)


#
# Change logging
#

class ObjectChangeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:objectchange-detail')
    user = NestedUserSerializer(
        read_only=True
    )
    action = ChoiceField(
        choices=ObjectChangeActionChoices,
        read_only=True
    )
    changed_object_type = ContentTypeField(
        read_only=True
    )
    changed_object = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = ObjectChange
        fields = [
            'id', 'url', 'display', 'time', 'user', 'user_name', 'request_id', 'action', 'changed_object_type',
            'changed_object_id', 'changed_object', 'prechange_data', 'postchange_data',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_changed_object(self, obj):
        """
        Serialize a nested representation of the changed object.
        """
        if obj.changed_object is None:
            return None

        try:
            serializer = get_serializer_for_model(obj.changed_object, prefix='Nested')
        except SerializerNotFound:
            return obj.object_repr
        context = {
            'request': self.context['request']
        }
        data = serializer(obj.changed_object, context=context).data

        return data


#
# ContentTypes
#

class ContentTypeSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:contenttype-detail')

    class Meta:
        model = ContentType
        fields = ['id', 'url', 'display', 'app_label', 'model']
