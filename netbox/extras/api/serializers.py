from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from dcim.api.nested_serializers import (
    NestedDeviceRoleSerializer, NestedDeviceTypeSerializer, NestedLocationSerializer, NestedPlatformSerializer,
    NestedRegionSerializer, NestedSiteSerializer, NestedSiteGroupSerializer,
)
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from extras.utils import FeatureQuery
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import BaseModelSerializer, NetBoxModelSerializer, ValidatedModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.nested_serializers import NestedTenantSerializer, NestedTenantGroupSerializer
from tenancy.models import Tenant, TenantGroup
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import get_serializer_for_model
from virtualization.api.nested_serializers import (
    NestedClusterGroupSerializer, NestedClusterSerializer, NestedClusterTypeSerializer,
)
from virtualization.models import Cluster, ClusterGroup, ClusterType
from .nested_serializers import *

__all__ = (
    'ConfigContextSerializer',
    'ContentTypeSerializer',
    'CustomFieldSerializer',
    'CustomLinkSerializer',
    'ExportTemplateSerializer',
    'ImageAttachmentSerializer',
    'JobResultSerializer',
    'JournalEntrySerializer',
    'ObjectChangeSerializer',
    'ReportDetailSerializer',
    'ReportSerializer',
    'ReportInputSerializer',
    'SavedFilterSerializer',
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
            'conditions', 'ssl_verification', 'ca_file_path', 'created', 'last_updated',
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
    object_type = ContentTypeField(
        queryset=ContentType.objects.all(),
        required=False
    )
    filter_logic = ChoiceField(choices=CustomFieldFilterLogicChoices, required=False)
    data_type = serializers.SerializerMethodField()
    ui_visibility = ChoiceField(choices=CustomFieldVisibilityChoices, required=False)

    class Meta:
        model = CustomField
        fields = [
            'id', 'url', 'display', 'content_types', 'type', 'object_type', 'data_type', 'name', 'label', 'group_name',
            'description', 'required', 'search_weight', 'filter_logic', 'ui_visibility', 'default', 'weight',
            'validation_minimum', 'validation_maximum', 'validation_regex', 'choices', 'created', 'last_updated',
        ]

    def validate_type(self, value):
        if self.instance and self.instance.type != value:
            raise serializers.ValidationError('Changing the type of custom fields is not supported.')

        return value

    def get_data_type(self, obj):
        types = CustomFieldTypeChoices
        if obj.type == types.TYPE_INTEGER:
            return 'integer'
        if obj.type == types.TYPE_DECIMAL:
            return 'decimal'
        if obj.type == types.TYPE_BOOLEAN:
            return 'boolean'
        if obj.type in (types.TYPE_JSON, types.TYPE_OBJECT):
            return 'object'
        if obj.type in (types.TYPE_MULTISELECT, types.TYPE_MULTIOBJECT):
            return 'array'
        return 'string'


#
# Custom links
#

class CustomLinkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('custom_links').get_query()),
        many=True
    )

    class Meta:
        model = CustomLink
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'enabled', 'link_text', 'link_url', 'weight', 'group_name',
            'button_class', 'new_window', 'created', 'last_updated',
        ]


#
# Export templates
#

class ExportTemplateSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:exporttemplate-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.filter(FeatureQuery('export_templates').get_query()),
        many=True
    )

    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'description', 'template_code', 'mime_type',
            'file_extension', 'as_attachment', 'created', 'last_updated',
        ]


#
# Saved filters
#

class SavedFilterSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:savedfilter-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.all(),
        many=True
    )

    class Meta:
        model = SavedFilter
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'slug', 'description', 'user', 'weight', 'enabled',
            'shared', 'parameters', 'created', 'last_updated',
        ]


#
# Tags
#

class TagSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')
    tagged_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'tagged_items', 'created', 'last_updated',
        ]


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
            'image_width', 'created', 'last_updated',
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

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_parent(self, obj):
        serializer = get_serializer_for_model(obj.parent, prefix=NESTED_SERIALIZER_PREFIX)
        return serializer(obj.parent, context={'request': self.context['request']}).data


#
# Journal entries
#

class JournalEntrySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:journalentry-detail')
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=User.objects.all(),
        required=False,
        default=serializers.CurrentUserDefault()
    )
    kind = ChoiceField(
        choices=JournalEntryKindChoices,
        required=False
    )

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'url', 'display', 'assigned_object_type', 'assigned_object_id', 'assigned_object', 'created',
            'created_by', 'kind', 'comments', 'tags', 'custom_fields', 'last_updated',
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

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_assigned_object(self, instance):
        serializer = get_serializer_for_model(instance.assigned_object_type.model_class(), prefix=NESTED_SERIALIZER_PREFIX)
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
    locations = SerializedPKRelatedField(
        queryset=Location.objects.all(),
        serializer=NestedLocationSerializer,
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
    cluster_types = SerializedPKRelatedField(
        queryset=ClusterType.objects.all(),
        serializer=NestedClusterTypeSerializer,
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
            'locations', 'device_types', 'roles', 'platforms', 'cluster_types', 'cluster_groups', 'clusters',
            'tenant_groups', 'tenants', 'tags', 'data', 'created', 'last_updated',
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
            'id', 'url', 'display', 'status', 'created', 'scheduled', 'interval', 'started', 'completed', 'name',
            'obj_type', 'user', 'data', 'job_id',
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


class ReportInputSerializer(serializers.Serializer):
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    interval = serializers.IntegerField(required=False, allow_null=True)


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

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_vars(self, instance):
        return {
            k: v.__class__.__name__ for k, v in instance._get_vars().items()
        }


class ScriptDetailSerializer(ScriptSerializer):
    result = JobResultSerializer()


class ScriptInputSerializer(serializers.Serializer):
    data = serializers.JSONField()
    commit = serializers.BooleanField()
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    interval = serializers.IntegerField(required=False, allow_null=True)


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

    @swagger_serializer_method(serializer_or_field=serializers.JSONField)
    def get_changed_object(self, obj):
        """
        Serialize a nested representation of the changed object.
        """
        if obj.changed_object is None:
            return None

        try:
            serializer = get_serializer_for_model(obj.changed_object, prefix=NESTED_SERIALIZER_PREFIX)
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
