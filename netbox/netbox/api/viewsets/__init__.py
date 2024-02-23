import logging
from functools import cached_property

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError, RestrictedError
from django_pglocks import advisory_lock
from netbox.constants import ADVISORY_LOCK_KEYS
from rest_framework import mixins as drf_mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utilities.api import get_annotations_for_serializer, get_prefetches_for_serializer
from utilities.exceptions import AbortRequest
from . import mixins

__all__ = (
    'NetBoxReadOnlyModelViewSet',
    'NetBoxModelViewSet',
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
        if prefetch := get_prefetches_for_serializer(serializer_class, fields_to_include=self.requested_fields):
            qs = qs.prefetch_related(*prefetch)

        # Dynamically resolve annotations for RelatedObjectCountFields on the serializer and attach them to the queryset
        if annotations := get_annotations_for_serializer(serializer_class, fields_to_include=self.requested_fields):
            qs = qs.annotate(**annotations)

        return qs

    def get_serializer(self, *args, **kwargs):

        # If specific fields have been requested, pass them to the serializer
        if self.requested_fields:
            kwargs['requested_fields'] = self.requested_fields

        return super().get_serializer(*args, **kwargs)

    @cached_property
    def requested_fields(self):
        # An explicit list of fields was requested
        if requested_fields := self.request.query_params.get('fields'):
            return requested_fields.split(',')
        # Brief mode has been enabled for this request
        elif self.brief:
            serializer_class = self.get_serializer_class()
            return getattr(serializer_class.Meta, 'brief_fields', None)
        return None


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

    def perform_create(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Creating new {model._meta.verbose_name}")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Updates

    def update(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Updating {model._meta.verbose_name} {serializer.instance} (PK: {serializer.instance.pk})")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Deletes

    def destroy(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().destroy(request, *args, **kwargs)

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
