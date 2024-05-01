from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import ListField

from core.api.nested_serializers import NestedDataSourceSerializer, NestedDataFileSerializer, NestedJobSerializer
from core.api.serializers import JobSerializer
from core.models import ContentType
from dcim.api.nested_serializers import (
    NestedDeviceRoleSerializer, NestedDeviceTypeSerializer, NestedLocationSerializer, NestedPlatformSerializer,
    NestedRegionSerializer, NestedSiteSerializer, NestedSiteGroupSerializer,
)
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.choices import *
from extras.models import *
from netbox.api.exceptions import SerializerNotFound
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import BaseModelSerializer, NetBoxModelSerializer, ValidatedModelSerializer
from netbox.api.serializers.features import TaggableModelSerializer
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
    'BookmarkSerializer',
    'ConfigContextSerializer',
    'ConfigTemplateSerializer',
    'ContentTypeSerializer',
    'CustomFieldChoiceSetSerializer',
    'CustomFieldSerializer',
    'CustomLinkSerializer',
    'DashboardSerializer',
    'EventRuleSerializer',
    'ExportTemplateSerializer',
    'ImageAttachmentSerializer',
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
# Event Rules
#

class EventRuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:eventrule-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('event_rules'),
        many=True
    )
    action_type = ChoiceField(choices=EventRuleActionChoices)
    action_object_type = ContentTypeField(
        queryset=ContentType.objects.with_feature('event_rules'),
    )
    action_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventRule
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'type_create', 'type_update', 'type_delete',
            'type_job_start', 'type_job_end', 'enabled', 'conditions', 'action_type', 'action_object_type',
            'action_object_id', 'action_object', 'description', 'custom_fields', 'tags', 'created', 'last_updated',
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_action_object(self, instance):
        context = {'request': self.context['request']}
        # We need to manually instantiate the serializer for scripts
        if instance.action_type == EventRuleActionChoices.SCRIPT:
            script_name = instance.action_parameters['script_name']
            if script_name in instance.action_object.scripts:
                script = instance.action_object.scripts[script_name]()
                return NestedScriptSerializer(script, context=context).data
            else:
                return None
        else:
            serializer = get_serializer_for_model(
                model=instance.action_object_type.model_class(),
                prefix=NESTED_SERIALIZER_PREFIX
            )
            return serializer(instance.action_object, context=context).data


#
# Webhooks
#

class WebhookSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:webhook-detail')

    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'display', 'name', 'description', 'payload_url', 'http_method', 'http_content_type',
            'additional_headers', 'body_template', 'secret', 'ssl_verification', 'ca_file_path', 'custom_fields',
            'tags', 'created', 'last_updated',
        ]


#
# Custom fields
#

class CustomFieldSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfield-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('custom_fields'),
        many=True
    )
    type = ChoiceField(choices=CustomFieldTypeChoices)
    object_type = ContentTypeField(
        queryset=ContentType.objects.all(),
        required=False,
        allow_null=True
    )
    filter_logic = ChoiceField(choices=CustomFieldFilterLogicChoices, required=False)
    data_type = serializers.SerializerMethodField()
    choice_set = NestedCustomFieldChoiceSetSerializer(
        required=False,
        allow_null=True
    )
    ui_visible = ChoiceField(choices=CustomFieldUIVisibleChoices, required=False)
    ui_editable = ChoiceField(choices=CustomFieldUIEditableChoices, required=False)

    class Meta:
        model = CustomField
        fields = [
            'id', 'url', 'display', 'content_types', 'type', 'object_type', 'data_type', 'name', 'label', 'group_name',
            'description', 'required', 'search_weight', 'filter_logic', 'ui_visible', 'ui_editable', 'is_cloneable',
            'default', 'weight', 'validation_minimum', 'validation_maximum', 'validation_regex', 'choice_set',
            'created', 'last_updated',
        ]

    def validate_type(self, value):
        if self.instance and self.instance.type != value:
            raise serializers.ValidationError(_('Changing the type of custom fields is not supported.'))

        return value

    @extend_schema_field(OpenApiTypes.STR)
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


class CustomFieldChoiceSetSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfieldchoiceset-detail')
    base_choices = ChoiceField(
        choices=CustomFieldChoiceSetBaseChoices,
        required=False
    )
    extra_choices = serializers.ListField(
        child=serializers.ListField(
            min_length=2,
            max_length=2
        )
    )

    class Meta:
        model = CustomFieldChoiceSet
        fields = [
            'id', 'url', 'display', 'name', 'description', 'base_choices', 'extra_choices', 'order_alphabetically',
            'choices_count', 'created', 'last_updated',
        ]


#
# Custom links
#

class CustomLinkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customlink-detail')
    content_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('custom_links'),
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
        queryset=ContentType.objects.with_feature('export_templates'),
        many=True
    )
    data_source = NestedDataSourceSerializer(
        required=False
    )
    data_file = NestedDataFileSerializer(
        read_only=True
    )

    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'url', 'display', 'content_types', 'name', 'description', 'template_code', 'mime_type',
            'file_extension', 'as_attachment', 'data_source', 'data_path', 'data_file', 'data_synced', 'created',
            'last_updated',
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
# Bookmarks
#

class BookmarkSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:bookmark-detail')
    object_type = ContentTypeField(
        queryset=ContentType.objects.with_feature('bookmarks'),
    )
    object = serializers.SerializerMethodField(read_only=True)
    user = NestedUserSerializer()

    class Meta:
        model = Bookmark
        fields = [
            'id', 'url', 'display', 'object_type', 'object_id', 'object', 'user', 'created',
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.object, prefix=NESTED_SERIALIZER_PREFIX)
        return serializer(instance.object, context={'request': self.context['request']}).data


#
# Tags
#

class TagSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:tag-detail')
    object_types = ContentTypeField(
        queryset=ContentType.objects.with_feature('tags'),
        many=True,
        required=False
    )
    tagged_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'description', 'object_types', 'tagged_items', 'created',
            'last_updated',
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

    @extend_schema_field(serializers.JSONField(allow_null=True))
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
        queryset=get_user_model().objects.all(),
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

    @extend_schema_field(serializers.JSONField(allow_null=True))
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
    data_source = NestedDataSourceSerializer(
        required=False
    )
    data_file = NestedDataFileSerializer(
        read_only=True
    )

    class Meta:
        model = ConfigContext
        fields = [
            'id', 'url', 'display', 'name', 'weight', 'description', 'is_active', 'regions', 'site_groups', 'sites',
            'locations', 'device_types', 'roles', 'platforms', 'cluster_types', 'cluster_groups', 'clusters',
            'tenant_groups', 'tenants', 'tags', 'data_source', 'data_path', 'data_file', 'data_synced', 'data',
            'created', 'last_updated',
        ]


#
# Config templates
#

class ConfigTemplateSerializer(TaggableModelSerializer, ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configtemplate-detail')
    data_source = NestedDataSourceSerializer(
        required=False
    )
    data_file = NestedDataFileSerializer(
        required=False
    )

    class Meta:
        model = ConfigTemplate
        fields = [
            'id', 'url', 'display', 'name', 'description', 'environment_params', 'template_code', 'data_source',
            'data_path', 'data_file', 'data_synced', 'tags', 'created', 'last_updated',
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
    test_methods = serializers.ListField(child=serializers.CharField(max_length=255), read_only=True)
    result = NestedJobSerializer()
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.CharField())
    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'


class ReportDetailSerializer(ReportSerializer):
    result = JobSerializer()


class ReportInputSerializer(serializers.Serializer):
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    interval = serializers.IntegerField(required=False, allow_null=True)

    def validate_schedule_at(self, value):
        if value and not self.context['report'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this report."))
        return value

    def validate_interval(self, value):
        if value and not self.context['report'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this report."))
        return value


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
    result = NestedJobSerializer()
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_vars(self, instance):
        return {
            k: v.__class__.__name__ for k, v in instance._get_vars().items()
        }

    @extend_schema_field(serializers.CharField())
    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'


class ScriptDetailSerializer(ScriptSerializer):
    result = JobSerializer()


class ScriptInputSerializer(serializers.Serializer):
    data = serializers.JSONField()
    commit = serializers.BooleanField()
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    interval = serializers.IntegerField(required=False, allow_null=True)

    def validate_schedule_at(self, value):
        if value and not self.context['script'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this script."))
        return value

    def validate_interval(self, value):
        if value and not self.context['script'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this script."))
        return value


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

    @extend_schema_field(serializers.JSONField(allow_null=True))
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


#
# User dashboard
#

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ('layout', 'config')
