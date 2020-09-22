import logging
from collections import OrderedDict

import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, MultipleObjectsReturned, ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import ManyToManyField, ProtectedError
from django.urls import reverse
from rest_framework import mixins, serializers, status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.relations import PrimaryKeyRelatedField, RelatedField
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import GenericViewSet

from .utils import dict_to_filter_params, dynamic_import

HTTP_ACTIONS = {
    'GET': 'view',
    'OPTIONS': None,
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


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
    # Serializers for Django's auth models are in the users app
    if app_name == 'auth':
        app_name = 'users'
    serializer_name = f'{app_name}.api.serializers.{prefix}{model_name}Serializer'
    try:
        return dynamic_import(serializer_name)
    except AttributeError:
        raise SerializerNotFound(
            "Could not determine serializer for {}.{} with prefix '{}'".format(app_name, model_name, prefix)
        )


def is_api_request(request):
    """
    Return True of the request is being made via the REST API.
    """
    api_path = reverse('api-root')
    return request.path_info.startswith(api_path)


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

class ChoiceField(serializers.Field):
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
        return OrderedDict([
            ('value', obj),
            ('label', self._choices[obj])
        ])

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
        except TypeError:  # Input is an unhashable type
            pass

        raise ValidationError(f"{data} is not a valid choice.")

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


class TimeZoneField(serializers.Field):
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
class ValidatedModelSerializer(serializers.ModelSerializer):
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
        instance.validate_unique()

        return data


class WritableNestedSerializer(serializers.ModelSerializer):
    """
    Returns a nested representation of an object on read, but accepts only a primary key on write.
    """

    def to_internal_value(self, data):

        if data is None:
            return None

        # Dictionary of related object attributes
        if isinstance(data, dict):
            params = dict_to_filter_params(data)
            queryset = self.Meta.model.objects
            try:
                return queryset.get(**params)
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
        queryset = self.Meta.model.objects
        try:
            return queryset.get(pk=int(data))
        except ObjectDoesNotExist:
            raise ValidationError(
                "Related object not found using the provided numeric ID: {}".format(pk)
            )


class BulkOperationSerializer(serializers.Serializer):
    id = serializers.IntegerField()


#
# Mixins
#

class BulkUpdateModelMixin:
    """
    Support bulk modification of objects using the list endpoint for a model. Accepts a PATCH action with a list of one
    or more JSON objects, each specifying the numeric ID of an object to be updated as well as the attributes to be set.
    For example:

    PATCH /api/dcim/sites/
    [
        {
            "id": 123,
            "name": "New name"
        },
        {
            "id": 456,
            "status": "planned"
        }
    ]
    """
    def bulk_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        # Map update data by object ID
        update_data = {
            obj.pop('id'): obj for obj in request.data
        }

        self.perform_bulk_update(qs, update_data, partial=partial)

        return Response(status=status.HTTP_200_OK)

    def perform_bulk_update(self, objects, update_data, partial):
        with transaction.atomic():
            for obj in objects:
                data = update_data.get(obj.id)
                serializer = self.get_serializer(obj, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

    def bulk_partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.bulk_update(request, *args, **kwargs)


class BulkDestroyModelMixin:
    """
    Support bulk deletion of objects using the list endpoint for a model. Accepts a DELETE action with a list of one
    or more JSON objects, each specifying the numeric ID of an object to be deleted. For example:

    DELETE /api/dcim/sites/
    [
        {"id": 123},
        {"id": 456}
    ]
    """
    def bulk_destroy(self, request, *args, **kwargs):
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        self.perform_bulk_destroy(qs)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, objects):
        with transaction.atomic():
            for obj in objects:
                self.perform_destroy(obj)


#
# Viewsets
#

class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   BulkUpdateModelMixin,
                   BulkDestroyModelMixin,
                   GenericViewSet):
    """
    Accept either a single object or a list of objects to create.
    """
    def get_serializer(self, *args, **kwargs):

        # If a list of objects has been provided, initialize the serializer with many=True
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        logger = logging.getLogger('netbox.api.views.ModelViewSet')

        # If 'brief' has been passed as a query param, find and return the nested serializer for this model, if one
        # exists
        request = self.get_serializer_context()['request']
        if request.query_params.get('brief'):
            logger.debug("Request is for 'brief' format; initializing nested serializer")
            try:
                serializer = get_serializer_for_model(self.queryset.model, prefix='Nested')
                logger.debug(f"Using serializer {serializer}")
                return serializer
            except SerializerNotFound:
                pass

        # Fall back to the hard-coded serializer class
        logger.debug(f"Using serializer {self.serializer_class}")
        return self.serializer_class

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return

        # Restrict the view's QuerySet to allow only the permitted objects
        action = HTTP_ACTIONS[request.method]
        if action:
            self.queryset = self.queryset.restrict(request.user, action)

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger('netbox.api.views.ModelViewSet')

        try:
            return super().dispatch(request, *args, **kwargs)
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            msg = f'Unable to delete object. {len(protected_objects)} dependent objects were found: '
            msg += ', '.join([f'{obj} ({obj.pk})' for obj in protected_objects])
            logger.warning(msg)
            return self.finalize_response(
                request,
                Response({'detail': msg}, status=409),
                *args,
                **kwargs
            )

    def _validate_objects(self, instance):
        """
        Check that the provided instance or list of instances are matched by the current queryset. This confirms that
        any newly created or modified objects abide by the attributes granted by any applicable ObjectPermissions.
        """
        if type(instance) is list:
            # Check that all instances are still included in the view's queryset
            conforming_count = self.queryset.filter(pk__in=[obj.pk for obj in instance]).count()
            if conforming_count != len(instance):
                raise ObjectDoesNotExist
        else:
            # Check that the instance is matched by the view's queryset
            self.queryset.get(pk=instance.pk)

    def perform_create(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Creating new {model._meta.verbose_name}")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    def perform_update(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Updating {model._meta.verbose_name} {serializer.instance} (PK: {serializer.instance.pk})")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    def perform_destroy(self, instance):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Deleting {model._meta.verbose_name} {instance} (PK: {instance.pk})")

        return super().perform_destroy(instance)


#
# Routers
#

class OrderedDefaultRouter(DefaultRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Extend the list view mappings to support the DELETE operation
        self.routes[0].mapping.update({
            'put': 'bulk_update',
            'patch': 'bulk_partial_update',
            'delete': 'bulk_destroy',
        })

    def get_api_root_view(self, api_urls=None):
        """
        Wrap DRF's DefaultRouter to return an alphabetized list of endpoints.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in sorted(self.registry, key=lambda x: x[0]):
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)
