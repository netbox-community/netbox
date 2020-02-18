from collections import OrderedDict

import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import ManyToManyField, ProtectedError
from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from rest_framework.relations import PrimaryKeyRelatedField, RelatedField
from rest_framework.response import Response
from rest_framework.serializers import Field, ModelSerializer, ValidationError
from rest_framework.viewsets import ModelViewSet as _ModelViewSet, ViewSet

from .utils import dict_to_filter_params, dynamic_import


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, please try again later."


class SerializerNotFound(Exception):
    pass


def get_serializer_for_model(model, prefix=''):
    """
    Dynamically resolve and return the appropriate serializer for a model.
    """
    app_name, model_name = model._meta.label.split('.')
    serializer_name = '{}.api.serializers.{}{}Serializer'.format(
        app_name, prefix, model_name
    )
    try:
        return dynamic_import(serializer_name)
    except AttributeError:
        raise SerializerNotFound(
            "Could not determine serializer for {}.{} with prefix '{}'".format(app_name, model_name, prefix)
        )


#
# Authentication
#

class IsAuthenticatedOrLoginNotRequired(BasePermission):
    """
    Returns True if the user is authenticated or LOGIN_REQUIRED is False.
    """
    def has_permission(self, request, view):
        if not settings.LOGIN_REQUIRED:
            return True
        return request.user.is_authenticated


#
# Fields
#

class ChoiceField(Field):
    """
    Represent a ChoiceField as {'value': <DB value>, 'label': <string>}. Accepts a single value on write.

    :param choices: An iterable of choices in the form (value, key).
    :param allow_blank: Allow blank values in addition to the listed choices.
    """
    def __init__(self, choices, allow_blank=False, **kwargs):
        self.choiceset = choices
        self.allow_blank = allow_blank
        self._choices = dict()

        # Unpack grouped choices
        for k, v in choices:
            if type(v) in [list, tuple]:
                for k2, v2 in v:
                    self._choices[k2] = v2
            else:
                self._choices[k] = v

        super().__init__(**kwargs)

    def validate_empty_values(self, data):
        # Convert null to an empty string unless allow_null == True
        if data is None:
            if self.allow_null:
                return True, None
            else:
                data = ''
        return super().validate_empty_values(data)

    def to_representation(self, obj):
        if obj is '':
            return None
        data = OrderedDict([
            ('value', obj),
            ('label', self._choices[obj])
        ])

        # TODO: Remove in v2.8
        # Include legacy numeric ID (where applicable)
        if hasattr(self.choiceset, 'LEGACY_MAP') and obj in self.choiceset.LEGACY_MAP:
            data['id'] = self.choiceset.LEGACY_MAP.get(obj)

        return data

    def to_internal_value(self, data):
        if data is '':
            if self.allow_blank:
                return data
            raise ValidationError("This field may not be blank.")

        # Provide an explicit error message if the request is trying to write a dict or list
        if isinstance(data, (dict, list)):
            raise ValidationError('Value must be passed directly (e.g. "foo": 123); do not use a dictionary or list.')

        # Check for string representations of boolean/integer values
        if hasattr(data, 'lower'):
            if data.lower() == 'true':
                data = True
            elif data.lower() == 'false':
                data = False
            else:
                try:
                    data = int(data)
                except ValueError:
                    pass

        try:
            if data in self._choices:
                return data
            # Check if data is a legacy numeric ID
            slug = self.choiceset.id_to_slug(data)
            if slug is not None:
                return slug
        except TypeError:  # Input is an unhashable type
            pass

        raise ValidationError("{} is not a valid choice.".format(data))

    @property
    def choices(self):
        return self._choices


class ContentTypeField(RelatedField):
    """
    Represent a ContentType as '<app_label>.<model>'
    """
    default_error_messages = {
        "does_not_exist": "Invalid content type: {content_type}",
        "invalid": "Invalid value. Specify a content type as '<app_label>.<model_name>'.",
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split('.')
            return ContentType.objects.get_by_natural_key(app_label=app_label, model=model)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', content_type=data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, obj):
        return "{}.{}".format(obj.app_label, obj.model)


class TimeZoneField(Field):
    """
    Represent a pytz time zone.
    """
    def to_representation(self, obj):
        return obj.zone if obj else None

    def to_internal_value(self, data):
        if not data:
            return ""
        if data not in pytz.common_timezones:
            raise ValidationError('Unknown time zone "{}" (see pytz.common_timezones for all options)'.format(data))
        return pytz.timezone(data)


class SerializedPKRelatedField(PrimaryKeyRelatedField):
    """
    Extends PrimaryKeyRelatedField to return a serialized object on read. This is useful for representing related
    objects in a ManyToManyField while still allowing a set of primary keys to be written.
    """
    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer(value, context={'request': self.context['request']}).data


#
# Serializers
#

# TODO: We should probably take a fresh look at exactly what we're doing with this. There might be a more elegant
# way to enforce model validation on the serializer.
class ValidatedModelSerializer(ModelSerializer):
    """
    Extends the built-in ModelSerializer to enforce calling clean() on the associated model during validation.
    """
    def validate(self, data):

        # Remove custom fields data and tags (if any) prior to model validation
        attrs = data.copy()
        attrs.pop('custom_fields', None)
        attrs.pop('tags', None)

        # Skip ManyToManyFields
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, ManyToManyField):
                attrs.pop(field.name, None)

        # Run clean() on an instance of the model
        if self.instance is None:
            instance = self.Meta.model(**attrs)
        else:
            instance = self.instance
            for k, v in attrs.items():
                setattr(instance, k, v)
        instance.clean()

        return data


class WritableNestedSerializer(ModelSerializer):
    """
    Returns a nested representation of an object on read, but accepts only a primary key on write.
    """

    def to_internal_value(self, data):

        if data is None:
            return None

        # Dictionary of related object attributes
        if isinstance(data, dict):
            params = dict_to_filter_params(data)
            try:
                return self.Meta.model.objects.get(**params)
            except ObjectDoesNotExist:
                raise ValidationError(
                    "Related object not found using the provided attributes: {}".format(params)
                )
            except MultipleObjectsReturned:
                raise ValidationError(
                    "Multiple objects match the provided attributes: {}".format(params)
                )
            except FieldError as e:
                raise ValidationError(e)

        # Integer PK of related object
        if isinstance(data, int):
            pk = data
        else:
            try:
                # PK might have been mistakenly passed as a string
                pk = int(data)
            except (TypeError, ValueError):
                raise ValidationError(
                    "Related objects must be referenced by numeric ID or by dictionary of attributes. Received an "
                    "unrecognized value: {}".format(data)
                )

        # Look up object by PK
        try:
            return self.Meta.model.objects.get(pk=int(data))
        except ObjectDoesNotExist:
            raise ValidationError(
                "Related object not found using the provided numeric ID: {}".format(pk)
            )


#
# Viewsets
#

class ModelViewSet(_ModelViewSet):
    """
    Accept either a single object or a list of objects to create.
    """
    def get_serializer(self, *args, **kwargs):

        # If a list of objects has been provided, initialize the serializer with many=True
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def get_serializer_class(self):

        # If 'brief' has been passed as a query param, find and return the nested serializer for this model, if one
        # exists
        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            try:
                return get_serializer_for_model(self.queryset.model, prefix='Nested')
            except SerializerNotFound:
                pass

        # Fall back to the hard-coded serializer class
        return self.serializer_class

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ProtectedError as e:
            models = ['{} ({})'.format(o, o._meta) for o in e.protected_objects.all()]
            msg = 'Unable to delete object. The following dependent objects were found: {}'.format(', '.join(models))
            return self.finalize_response(
                request,
                Response({'detail': msg}, status=409),
                *args,
                **kwargs
            )

    def list(self, *args, **kwargs):
        """
        Call to super to allow for caching
        """
        return super().list(*args, **kwargs)

    def retrieve(self, *args, **kwargs):
        """
        Call to super to allow for caching
        """
        return super().retrieve(*args, **kwargs)


class FieldChoicesViewSet(ViewSet):
    """
    Expose the built-in numeric values which represent static choices for a model's field.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]
    fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Compile a dict of all fields in this view
        self._fields = OrderedDict()
        for serializer_class, field_list in self.fields:
            for field_name in field_list:

                model_name = serializer_class.Meta.model._meta.verbose_name
                key = ':'.join([model_name.lower().replace(' ', '-'), field_name])
                serializer = serializer_class()
                choices = []

                for k, v in serializer.get_fields()[field_name].choices.items():
                    if type(v) in [list, tuple]:
                        for k2, v2 in v:
                            choices.append({
                                'value': k2,
                                'label': v2,
                            })
                    else:
                        choices.append({
                            'value': k,
                            'label': v,
                        })
                self._fields[key] = choices

    def list(self, request):
        return Response(self._fields)

    def retrieve(self, request, pk):
        if pk not in self._fields:
            raise Http404
        return Response(self._fields[pk])

    def get_view_name(self):
        return "Field Choices"
