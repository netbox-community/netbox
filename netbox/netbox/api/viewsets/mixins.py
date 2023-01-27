import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from extras.models import ExportTemplate
from netbox.api.exceptions import SerializerNotFound
from netbox.api.serializers import BulkOperationSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model

__all__ = (
    'BriefModeMixin',
    'BulkUpdateModelMixin',
    'CustomFieldsMixin',
    'ExportTemplatesMixin',
    'BulkDestroyModelMixin',
    'ObjectValidationMixin',
)


class BriefModeMixin:
    """
    Enables brief mode support, so that the client can invoke a model's nested serializer by passing e.g.
        GET /api/dcim/sites/?brief=True
    """
    brief = False
    brief_prefetch_fields = []

    def initialize_request(self, request, *args, **kwargs):
        # Annotate whether brief mode is active
        self.brief = request.method == 'GET' and request.GET.get('brief')

        return super().initialize_request(request, *args, **kwargs)

    def get_serializer_class(self):
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')

        # If using 'brief' mode, find and return the nested serializer for this model, if one exists
        if self.brief:
            logger.debug("Request is for 'brief' format; initializing nested serializer")
            try:
                return get_serializer_for_model(self.queryset.model, prefix=NESTED_SERIALIZER_PREFIX)
            except SerializerNotFound:
                logger.debug(
                    f"Nested serializer for {self.queryset.model} not found! Using serializer {self.serializer_class}"
                )

        return self.serializer_class

    def get_queryset(self):
        qs = super().get_queryset()

        # If using brief mode, clear all prefetches from the queryset and append only brief_prefetch_fields (if any)
        if self.brief:
            return qs.prefetch_related(None).prefetch_related(*self.brief_prefetch_fields)

        return qs


class CustomFieldsMixin:
    """
    For models which support custom fields, populate the `custom_fields` context.
    """
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if hasattr(self.queryset.model, 'custom_fields'):
            content_type = ContentType.objects.get_for_model(self.queryset.model)
            context.update({
                'custom_fields': content_type.custom_fields.all(),
            })

        return context


class ExportTemplatesMixin:
    """
    Enable ExportTemplate support for list views.
    """
    def list(self, request, *args, **kwargs):
        if 'export' in request.GET:
            content_type = ContentType.objects.get_for_model(self.get_serializer_class().Meta.model)
            et = ExportTemplate.objects.filter(content_types=content_type, name=request.GET['export']).first()
            if et is None:
                raise Http404
            queryset = self.filter_queryset(self.get_queryset())
            return et.render_to_response(queryset)

        return super().list(request, *args, **kwargs)


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

        data = self.perform_bulk_update(qs, update_data, partial=partial)

        return Response(data, status=status.HTTP_200_OK)

    def perform_bulk_update(self, objects, update_data, partial):
        with transaction.atomic():
            data_list = []
            for obj in objects:
                data = update_data.get(obj.id)
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                serializer = self.get_serializer(obj, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                data_list.append(serializer.data)

            return data_list

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
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                self.perform_destroy(obj)


class ObjectValidationMixin:

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
        elif not self.queryset.filter(pk=instance.pk).exists():
            raise ObjectDoesNotExist
