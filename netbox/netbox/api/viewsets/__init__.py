import logging
from functools import cached_property

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import router, transaction
from django.db.models import ProtectedError, RestrictedError
from django_pglocks import advisory_lock
from rest_framework import mixins as drf_mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from netbox.api.serializers.features import ChangeLogMessageSerializer
from netbox.constants import ADVISORY_LOCK_KEYS
from utilities.api import get_annotations_for_serializer, get_prefetches_for_serializer
from utilities.exceptions import AbortRequest
from utilities.query import reapply_model_ordering

from . import mixins

__all__ = (
    'NetBoxModelViewSet',
    'NetBoxReadOnlyModelViewSet',
)

HTTP_ACTIONS = {
    'GET': 'view',
    'OPTIONS': None,
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class BaseViewSet(GenericViewSet):
    """
    Base class for all API ViewSets. This is responsible for the enforcement of object-based permissions.
    """
    brief = False

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        # Restrict the view's QuerySet to allow only the permitted objects
        if request.user.is_authenticated:
            if action := HTTP_ACTIONS[request.method]:
                self.queryset = self.queryset.restrict(request.user, action)

    def initialize_request(self, request, *args, **kwargs):

        # Annotate whether brief mode is active
        self.brief = request.method == 'GET' and request.GET.get('brief')

        return super().initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        serializer_class = self.get_serializer_class()

        # Dynamically resolve prefetches for included serializer fields and attach them to the queryset
        if prefetch := get_prefetches_for_serializer(serializer_class, **self.field_kwargs):
            qs = qs.prefetch_related(*prefetch)

        # Dynamically resolve annotations for RelatedObjectCountFields on the serializer and attach them to the queryset
        if annotations := get_annotations_for_serializer(serializer_class, **self.field_kwargs):
            qs = qs.annotate(**annotations)

        return qs

    def get_serializer(self, *args, **kwargs):
        # Pass the fields/omit kwargs (if specified by the request) to the serializer
        kwargs.update(**self.field_kwargs)
        return super().get_serializer(*args, **kwargs)

    @cached_property
    def field_kwargs(self):
        """Return a dictionary of keyword arguments to be passed when instantiating the serializer."""
        # An explicit list of fields was requested
        if requested_fields := self.request.query_params.get('fields'):
            return {'fields': requested_fields.split(',')}

        # An explicit list of fields to omit was requested
        if omit_fields := self.request.query_params.get('omit'):
            return {'omit': omit_fields.split(',')}

        # Brief mode has been enabled for this request
        if self.brief:
            serializer_class = self.get_serializer_class()
            if brief_fields := getattr(serializer_class.Meta, 'brief_fields', None):
                return {'fields': brief_fields}

        return {}


class NetBoxReadOnlyModelViewSet(
    mixins.CustomFieldsMixin,
    mixins.ExportTemplatesMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.ListModelMixin,
    BaseViewSet
):
    pass


class NetBoxModelViewSet(
    mixins.BulkUpdateModelMixin,
    mixins.BulkDestroyModelMixin,
    mixins.ObjectValidationMixin,
    mixins.CustomFieldsMixin,
    mixins.ExportTemplatesMixin,
    drf_mixins.CreateModelMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.UpdateModelMixin,
    drf_mixins.DestroyModelMixin,
    drf_mixins.ListModelMixin,
    BaseViewSet
):
    """
    Extend DRF's ModelViewSet to support bulk update and delete functions.
    """
    def get_object_with_snapshot(self):
        """
        Save a pre-change snapshot of the object immediately after retrieving it. This snapshot will be used to
        record the "before" data in the changelog.
        """
        obj = super().get_object()
        if hasattr(obj, 'snapshot'):
            obj.snapshot()
        return obj

    def get_queryset(self):
        qs = super().get_queryset()
        return reapply_model_ordering(qs)

    def get_serializer(self, *args, **kwargs):
        # If a list of objects has been provided, initialize the serializer with many=True
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')

        try:
            return super().dispatch(request, *args, **kwargs)
        except (ProtectedError, RestrictedError) as e:
            if type(e) is ProtectedError:
                protected_objects = list(e.protected_objects)
            else:
                protected_objects = list(e.restricted_objects)
            msg = f'Unable to delete object. {len(protected_objects)} dependent objects were found: '
            msg += ', '.join([f'{obj} ({obj.pk})' for obj in protected_objects])
            logger.warning(msg)
            return self.finalize_response(
                request,
                Response({'detail': msg}, status=409),
                *args,
                **kwargs
            )
        except AbortRequest as e:
            logger.debug(e.message)
            return self.finalize_response(
                request,
                Response({'detail': e.message}, status=400),
                *args,
                **kwargs
            )

    # Creates

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bulk_create = getattr(serializer, 'many', False)
        self.perform_create(serializer)

        # After creating the instance(s), re-initialize the serializer with a queryset
        # to ensure related objects are prefetched.
        if bulk_create:
            instance_pks = [obj.pk for obj in serializer.instance]
            # Order by PK to ensure that the ordering of objects in the response
            # matches the ordering of those in the request.
            qs = self.get_queryset().filter(pk__in=instance_pks).order_by('pk')
        else:
            qs = self.get_queryset().get(pk=serializer.instance.pk)

        # Re-serialize the instance(s) with prefetched data
        serializer = self.get_serializer(qs, many=bulk_create)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Creating new {model._meta.verbose_name}")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic(using=router.db_for_write(model)):
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Updates

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object_with_snapshot()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # After updating the instance, re-initialize the serializer with a queryset
        # to ensure related objects are prefetched.
        qs = self.get_queryset().get(pk=serializer.instance.pk)

        # Re-serialize the instance(s) with prefetched data
        serializer = self.get_serializer(qs)

        return Response(serializer.data)

    def perform_update(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Updating {model._meta.verbose_name} {serializer.instance} (PK: {serializer.instance.pk})")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic(using=router.db_for_write(model)):
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Deletes

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object_with_snapshot()

        # Attach changelog message (if any)
        serializer = ChangeLogMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance._changelog_message = serializer.validated_data.get('changelog_message')

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Deleting {model._meta.verbose_name} {instance} (PK: {instance.pk})")

        return super().perform_destroy(instance)


class MPTTLockedMixin:
    """
    Puts pglock on objects that derive from MPTTModel for parallel API calling.
    Note: If adding this to a view, must add the model name to ADVISORY_LOCK_KEYS
    """

    def create(self, request, *args, **kwargs):
        with advisory_lock(ADVISORY_LOCK_KEYS[self.queryset.model._meta.model_name]):
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        with advisory_lock(ADVISORY_LOCK_KEYS[self.queryset.model._meta.model_name]):
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        with advisory_lock(ADVISORY_LOCK_KEYS[self.queryset.model._meta.model_name]):
            return super().destroy(request, *args, **kwargs)
