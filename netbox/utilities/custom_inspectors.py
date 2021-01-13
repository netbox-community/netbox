from django.contrib.postgres.fields import JSONField
from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector, NotHandled, PaginatorInspector, SwaggerAutoSchema
from drf_yasg.utils import get_serializer_ref_name
from rest_framework.fields import ChoiceField
from rest_framework.relations import ManyRelatedField

from extras.api.customfields import CustomFieldsDataField
from netbox.api import ChoiceField, SerializedPKRelatedField, WritableNestedSerializer


class NetBoxSwaggerAutoSchema(SwaggerAutoSchema):
    writable_serializers = {}

    def get_operation_id(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys
        operation_id = self.overrides.get('operation_id', '')
        if not operation_id:
            # Overwrite the action for bulk update/bulk delete views to ensure they get an operation ID that's
            # unique from their single-object counterparts (see #3436)
            if operation_keys[-1] in ('delete', 'partial_update', 'update') and not self.view.detail:
                operation_keys[-1] = f'bulk_{operation_keys[-1]}'
            operation_id = '_'.join(operation_keys)

        return operation_id

    def get_request_serializer(self):
        serializer = super().get_request_serializer()

        if serializer is not None and self.method in self.implicit_body_methods:
            properties = {}
            for child_name, child in serializer.fields.items():
                if isinstance(child, (ChoiceField, WritableNestedSerializer)):
                    properties[child_name] = None
                elif isinstance(child, ManyRelatedField) and isinstance(child.child_relation, SerializedPKRelatedField):
                    properties[child_name] = None

            if properties:
                if type(serializer) not in self.writable_serializers:
                    writable_name = 'Writable' + type(serializer).__name__
                    meta_class = getattr(type(serializer), 'Meta', None)
                    if meta_class:
                        ref_name = 'Writable' + get_serializer_ref_name(serializer)
                        writable_meta = type('Meta', (meta_class,), {'ref_name': ref_name})
                        properties['Meta'] = writable_meta

                    self.writable_serializers[type(serializer)] = type(writable_name, (type(serializer),), properties)

                writable_class = self.writable_serializers[type(serializer)]
                serializer = writable_class()

        return serializer


class SerializedPKRelatedFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        if isinstance(field, SerializedPKRelatedField):
            return self.probe_field_inspectors(field.serializer(), ChildSwaggerType, use_references)

        return NotHandled


class ChoiceFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        # this returns a callable which extracts title, description and other stuff
        # https://drf-yasg.readthedocs.io/en/stable/_modules/drf_yasg/inspectors/base.html#FieldInspector._get_partial_types
        SwaggerType, _ = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, ChoiceField):
            choices = field._choices
            choice_value = list(choices.keys())
            choice_label = list(choices.values())
            value_schema = openapi.Schema(type=openapi.TYPE_STRING, enum=choice_value)

            if set([None] + choice_value) == {None, True, False}:
                # DeviceType.subdevice_role and Device.face need to be differentiated since they each have
                # subtly different values in their choice keys.
                # - subdevice_role and connection_status are booleans, although subdevice_role includes None
                # - face is an integer set {0, 1} which is easily confused with {False, True}
                schema_type = openapi.TYPE_STRING
                if all(type(x) == bool for x in [c for c in choice_value if c is not None]):
                    schema_type = openapi.TYPE_BOOLEAN
                value_schema = openapi.Schema(type=schema_type, enum=choice_value)
                value_schema['x-nullable'] = True

            if all(type(x) == int for x in [c for c in choice_value if c is not None]):
                # Change value_schema for IPAddressFamilyChoices, RackWidthChoices
                value_schema = openapi.Schema(type=openapi.TYPE_INTEGER, enum=choice_value)

            schema = SwaggerType(type=openapi.TYPE_OBJECT, required=["label", "value"], properties={
                "label": openapi.Schema(type=openapi.TYPE_STRING, enum=choice_label),
                "value": value_schema
            })

            return schema

        return NotHandled


class NullableBooleanFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):

        if isinstance(result, openapi.Schema) and isinstance(obj, ChoiceField) and result.type == 'boolean':
            keys = obj.choices.keys()
            if set(keys) == {None, True, False}:
                result['x-nullable'] = True
                result.type = 'boolean'

        return result


class CustomFieldsDataFieldInspector(FieldInspector):

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, CustomFieldsDataField) and swagger_object_type == openapi.Schema:
            return SwaggerType(type=openapi.TYPE_OBJECT)

        return NotHandled


class JSONFieldInspector(FieldInspector):
    """Required because by default, Swagger sees a JSONField as a string and not dict
    """
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, openapi.Schema) and isinstance(obj, JSONField):
            result.type = 'dict'
        return result


class NullablePaginatorInspector(PaginatorInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if method_name == 'get_paginated_response' and isinstance(result, openapi.Schema):
            next = result.properties['next']
            if isinstance(next, openapi.Schema):
                next['x-nullable'] = True
            previous = result.properties['previous']
            if isinstance(previous, openapi.Schema):
                previous['x-nullable'] = True

        return result
