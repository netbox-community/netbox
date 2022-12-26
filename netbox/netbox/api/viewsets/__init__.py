import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from extras.models import ExportTemplate
from netbox.api.exceptions import SerializerNotFound
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model
from utilities.exceptions import AbortRequest
from .mixins import *

__all__ = (
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


class NetBoxModelViewSet(BulkUpdateModelMixin, BulkDestroyModelMixin, ObjectValidationMixin, ModelViewSet):
    """
    Extend DRF's ModelViewSet to support bulk update and delete functions.
    """
    brief = False
    brief_prefetch_fields = []

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

    def get_serializer_class(self):
        logger = logging.getLogger('netbox.api.views.ModelViewSet')

        # If using 'brief' mode, find and return the nested serializer for this model, if one exists
        if self.brief:
            logger.debug("Request is for 'brief' format; initializing nested serializer")
            try:
                serializer = get_serializer_for_model(self.queryset.model, prefix=NESTED_SERIALIZER_PREFIX)
                logger.debug(f"Using serializer {serializer}")
                return serializer
            except SerializerNotFound:
                logger.debug(f"Nested serializer for {self.queryset.model} not found!")

        # Fall back to the hard-coded serializer class
        logger.debug(f"Using serializer {self.serializer_class}")
        return self.serializer_class

    def get_serializer_context(self):
        """
        For models which support custom fields, populate the `custom_fields` context.
        """
        context = super().get_serializer_context()

        if hasattr(self.queryset.model, 'custom_fields'):
            content_type = ContentType.objects.get_for_model(self.queryset.model)
            context.update({
                'custom_fields': content_type.custom_fields.all(),
            })

        return context

    def get_queryset(self):
        # If using brief mode, clear all prefetches from the queryset and append only brief_prefetch_fields (if any)
        if self.brief:
            return super().get_queryset().prefetch_related(None).prefetch_related(*self.brief_prefetch_fields)

        return super().get_queryset()

    def initialize_request(self, request, *args, **kwargs):
        # Check if brief=True has been passed
        if request.method == 'GET' and request.GET.get('brief'):
            self.brief = True

        return super().initialize_request(request, *args, **kwargs)

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
        except AbortRequest as e:
            logger.debug(e.message)
            return self.finalize_response(
                request,
                Response({'detail': e.message}, status=400),
                *args,
                **kwargs
            )

    def list(self, request, *args, **kwargs):
        # Overrides ListModelMixin to allow processing ExportTemplates.
        if 'export' in request.GET:
            content_type = ContentType.objects.get_for_model(self.get_serializer_class().Meta.model)
            et = ExportTemplate.objects.filter(content_types=content_type, name=request.GET['export']).first()
            if et is None:
                raise Http404
            queryset = self.filter_queryset(self.get_queryset())
            return et.render_to_response(queryset)

        return super().list(request, *args, **kwargs)

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

    def update(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().update(request, *args, **kwargs)

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

    def destroy(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        model = self.queryset.model
        logger = logging.getLogger('netbox.api.views.ModelViewSet')
        logger.info(f"Deleting {model._meta.verbose_name} {instance} (PK: {instance.pk})")

        return super().perform_destroy(instance)
