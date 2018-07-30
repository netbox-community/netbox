from drf_yasg import openapi
from drf_yasg.inspectors import FieldInspector, NotHandled, PaginatorInspector, FilterInspector
from rest_framework.fields import ChoiceField

from extras.api.customfields import CustomFieldsSerializer
from utilities.api import ChoiceField


class CustomChoiceFieldInspector(FieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        # this returns a callable which extracts title, description and other stuff
        # https://drf-yasg.readthedocs.io/en/stable/_modules/drf_yasg/inspectors/base.html#FieldInspector._get_partial_types
        SwaggerType, _ = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, ChoiceField):
            value_schema = openapi.Schema(type=openapi.TYPE_INTEGER)

            choices = list(field._choices.keys())
            if set([None] + choices) == {None, True, False}:
                # DeviceType.subdevice_role, Device.face and InterfaceConnection.connection_status all need to be
                # differentiated since they each have subtly different values in their choice keys.
                # - subdevice_role and connection_status are booleans, although subdevice_role includes None
                # - face is an integer set {0, 1} which is easily confused with {False, True}
                schema_type = openapi.TYPE_INTEGER
                if all(type(x) == bool for x in [c for c in choices if c is not None]):
                    schema_type = openapi.TYPE_BOOLEAN
                value_schema = openapi.Schema(type=schema_type)
                value_schema['x-nullable'] = True

            schema = SwaggerType(type=openapi.TYPE_OBJECT, required=["label", "value"], properties={
                "label": openapi.Schema(type=openapi.TYPE_STRING),
                "value": value_schema
            })

            return schema

        elif isinstance(field, CustomFieldsSerializer):
            schema = SwaggerType(type=openapi.TYPE_OBJECT)
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


class IdInFilterInspector(FilterInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, list):
            params = [p for p in result if isinstance(p, openapi.Parameter) and p.name == 'id__in']
            for p in params:
                p.type = 'string'

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
