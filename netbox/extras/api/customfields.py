from django.utils.translation import gettext as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import Field
from rest_framework.serializers import ListSerializer, ValidationError

from extras.choices import CustomFieldTypeChoices
from extras.constants import CUSTOMFIELD_EMPTY_VALUES
from extras.models import CustomField
from utilities.api import get_serializer_for_model

#
# Custom fields
#


def restrict_queryset(model, request):
    """
    Return a queryset for the given model, restricted to the objects the requesting user is
    permitted to view. If no request is available (e.g. during internal serialization) or the
    model's manager does not support restriction, the unrestricted queryset is returned.
    """
    manager = model.objects
    if request is not None and hasattr(manager, 'restrict'):
        return manager.restrict(request.user, 'view')
    return manager.all()


class CustomFieldDefaultValues:
    """
    Return a dictionary of all CustomFields assigned to the parent model and their default values.
    """
    requires_context = True

    def __call__(self, serializer_field):
        self.model = serializer_field.parent.Meta.model

        # Populate the default value for each CustomField on the model
        value = {}
        for field in CustomField.objects.get_for_model(self.model):
            if field.default is not None:
                value[field.name] = field.default
            else:
                value[field.name] = None

        return value


@extend_schema_field(OpenApiTypes.OBJECT)
class CustomFieldsDataField(Field):

    def _get_custom_fields(self):
        """
        Cache CustomFields assigned to this model to avoid redundant database queries
        """
        if not hasattr(self, '_custom_fields'):
            self._custom_fields = CustomField.objects.get_for_model(self.parent.Meta.model)
        return self._custom_fields

    def to_representation(self, obj):
        # TODO: Fix circular import
        from utilities.api import get_serializer_for_model
        data = {}
        cache = self.parent.context.get('cf_object_cache')
        request = self.parent.context.get('request')

        for cf in self._get_custom_fields():
            if cf.type in (
                CustomFieldTypeChoices.TYPE_OBJECT,
                CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            ):
                raw = obj.get(cf.name)
                model = cf.related_object_type.model_class()
                if raw is None:
                    value = None
                elif cache is not None:
                    # Use the pre-fetched (and permission-restricted) bulk cache populated by
                    # CustomFieldListSerializer
                    if cf.type == CustomFieldTypeChoices.TYPE_OBJECT:
                        value = cache.get((model, raw))
                    else:
                        value = [cache[(model, pk)] for pk in raw if (model, pk) in cache]
                else:
                    # No bulk cache available (single-object serialization); query directly,
                    # restricting to objects the requesting user is permitted to view
                    queryset = restrict_queryset(model, request)
                    if cf.type == CustomFieldTypeChoices.TYPE_OBJECT:
                        value = queryset.filter(pk=raw).first()
                    else:
                        value = list(queryset.filter(pk__in=raw))
            else:
                value = cf.deserialize(obj.get(cf.name))

            if value is not None and cf.type == CustomFieldTypeChoices.TYPE_OBJECT:
                serializer = get_serializer_for_model(cf.related_object_type.model_class())
                value = serializer(value, nested=True, context=self.parent.context).data
            elif value is not None and cf.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
                serializer = get_serializer_for_model(cf.related_object_type.model_class())
                value = serializer(value, nested=True, many=True, context=self.parent.context).data
            data[cf.name] = value

        return data

    def to_internal_value(self, data):
        if type(data) is not dict:
            raise ValidationError(
                "Invalid data format. Custom field data must be passed as a dictionary mapping field names to their "
                "values."
            )

        custom_fields = {cf.name: cf for cf in self._get_custom_fields()}

        # Reject any unknown custom field names
        invalid_fields = set(data) - set(custom_fields)
        if invalid_fields:
            raise ValidationError({
                field: _("Custom field '{name}' does not exist for this object type.").format(name=field)
                for field in sorted(invalid_fields)
            })

        # Serialize object and multi-object values
        for cf in custom_fields.values():
            if cf.name in data and data[cf.name] not in CUSTOMFIELD_EMPTY_VALUES and cf.type in (
                    CustomFieldTypeChoices.TYPE_OBJECT,
                    CustomFieldTypeChoices.TYPE_MULTIOBJECT
            ):
                serializer_class = get_serializer_for_model(cf.related_object_type.model_class())
                many = cf.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT
                serializer = serializer_class(data=data[cf.name], nested=True, many=many, context=self.parent.context)
                if serializer.is_valid():
                    data[cf.name] = [obj['id'] for obj in serializer.data] if many else serializer.data['id']
                else:
                    raise ValidationError(_("Unknown related object(s): {name}").format(name=data[cf.name]))

        # If updating an existing instance, start with existing custom_field_data
        if self.parent.instance:
            data = {**self.parent.instance.custom_field_data, **data}

        return data


class CustomFieldListSerializer(ListSerializer):
    """
    ListSerializer that pre-fetches all OBJECT/MULTIOBJECT custom field related objects
    in bulk before per-item serialization.
    """
    def to_representation(self, data):
        cf_field = self.child.fields.get('custom_fields')
        if isinstance(cf_field, CustomFieldsDataField):
            request = self.context.get('request')
            object_type_cfs = [
                cf for cf in cf_field._get_custom_fields()
                if cf.type in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT)
            ]
            cache = {}
            for cf in object_type_cfs:
                model = cf.related_object_type.model_class()
                pks = set()
                for item in data:
                    raw = item.custom_field_data.get(cf.name)
                    if raw is not None:
                        if cf.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
                            pks.update(raw)
                        else:
                            pks.add(raw)
                # Restrict to objects the requesting user is permitted to view
                for obj in restrict_queryset(model, request).filter(pk__in=pks):
                    cache[(model, obj.pk)] = obj
            self.child.context['cf_object_cache'] = cache
        return super().to_representation(data)
