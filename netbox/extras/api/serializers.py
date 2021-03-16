from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from dcim.api.nested_serializers import (
    NestedDeviceSerializer, NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedRackSerializer,
    NestedRegionSerializer, NestedSiteSerializer,
)
from dcim.models import Device, DeviceRole, Platform, Rack, Region, Site
from extras.choices import *
from extras.models import (
    ConfigContext, CustomField, ExportTemplate, ImageAttachment, ObjectChange, JobResult, Tag,
)
from extras.utils import FeatureQuery
from netbox.api import ChoiceField, ContentTypeField, SerializedPKRelatedField, ValidatedModelSerializer
from netbox.api.exceptions import SerializerNotFound
from tenancy.api.nested_serializers import NestedTenantSerializer, NestedTenantGroupSerializer
from tenancy.models import Tenant, TenantGroup
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import get_serializer_for_model
from virtualization.api.nested_serializers import NestedClusterGroupSerializer, NestedClusterSerializer
from virtualization.models import Cluster, ClusterGroup
from .nested_serializers import *


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
            'id', 'url', 'content_types', 'type', 'name', 'label', 'description', 'required', 'filter_logic',
            'default', 'weight', 'validation_minimum', 'validation_maximum', 'validation_regex', 'choices',
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
        fields = ['id', 'url', 'content_type', 'name', 'description', 'template_code', 'mime_type', 'file_extension']


#
# Tags
#

class TagSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')
    tagged_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'url', 'name', 'slug', 'color', 'description', 'tagged_items']


class TaggedObjectSerializer(serializers.Serializer):
    tags = NestedTagSerializer(many=True, required=False)

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        instance = super().create(validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        # Cache tags on instance for change logging
        instance._tags = tags or []

        instance = super().update(instance, validated_data)

        if tags is not None:
            return self._save_tags(instance, tags)
        return instance

    def _save_tags(self, instance, tags):
        if tags:
            instance.tags.set(*[t.name for t in tags])
        else:
            instance.tags.clear()

        return instance


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
            'id', 'url', 'content_type', 'object_id', 'parent', 'name', 'image', 'image_height', 'image_width',
            'created',
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
    sites = SerializedPKRelatedField(
        queryset=Site.objects.all(),
        serializer=NestedSiteSerializer,
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
            'id', 'url', 'name', 'weight', 'description', 'is_active', 'regions', 'sites', 'roles', 'platforms',
            'cluster_groups', 'clusters', 'tenant_groups', 'tenants', 'tags', 'data', 'created', 'last_updated',
        ]


#
# Job Results
#

class JobResultSerializer(serializers.ModelSerializer):
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
            'id', 'url', 'created', 'completed', 'name', 'obj_type', 'status', 'user', 'data', 'job_id',
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

class ObjectChangeSerializer(serializers.ModelSerializer):
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
            'id', 'url', 'time', 'user', 'user_name', 'request_id', 'action', 'changed_object_type',
            'changed_object_id', 'changed_object', 'object_data',
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

class ContentTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:contenttype-detail')
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = ['id', 'url', 'app_label', 'model', 'display_name']

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_display_name(self, obj):
        return obj.app_labeled_name
