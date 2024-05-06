from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from extras.choices import *
from extras.models import CustomField, CustomFieldChoiceSet
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'CustomFieldChoiceSetSerializer',
    'CustomFieldSerializer',
)


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
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'choices_count')


class CustomFieldSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:customfield-detail')
    object_types = ContentTypeField(
        queryset=ObjectType.objects.with_feature('custom_fields'),
        many=True
    )
    type = ChoiceField(choices=CustomFieldTypeChoices)
    related_object_type = ContentTypeField(
        queryset=ObjectType.objects.all(),
        required=False,
        allow_null=True
    )
    filter_logic = ChoiceField(choices=CustomFieldFilterLogicChoices, required=False)
    data_type = serializers.SerializerMethodField()
    choice_set = CustomFieldChoiceSetSerializer(
        nested=True,
        required=False,
        allow_null=True
    )
    ui_visible = ChoiceField(choices=CustomFieldUIVisibleChoices, required=False)
    ui_editable = ChoiceField(choices=CustomFieldUIEditableChoices, required=False)

    class Meta:
        model = CustomField
        fields = [
            'id', 'url', 'display', 'object_types', 'type', 'related_object_type', 'data_type', 'name', 'label',
            'group_name', 'description', 'required', 'search_weight', 'filter_logic', 'ui_visible', 'ui_editable',
            'is_cloneable', 'default', 'weight', 'validation_minimum', 'validation_maximum', 'validation_regex',
            'choice_set', 'comments', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

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
