from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from core.models import ObjectType
from extras.models import ExportTemplate
from netbox.api.serializers import BulkOperationSerializer

__all__ = (
    'BulkDestroyModelMixin',
    'BulkUpdateModelMixin',
    'CustomFieldsMixin',
    'ExportTemplatesMixin',
    'ObjectValidationMixin',
    'SequentialBulkCreatesMixin',
)


class CustomFieldsMixin:
    """
    For models which support custom fields, populate the `custom_fields` context.
    """
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if hasattr(self.queryset.model, 'custom_fields'):
            object_type = ObjectType.objects.get_for_model(self.queryset.model)
            context.update({
                'custom_fields': object_type.custom_fields.all(),
            })

        return context


class ExportTemplatesMixin:
    """
    Enable ExportTemplate support for list views.
    """
    def list(self, request, *args, **kwargs):
        if 'export' in request.GET:
            object_type = ObjectType.objects.get_for_model(self.get_serializer_class().Meta.model)
            et = ExportTemplate.objects.filter(object_types=object_type, name=request.GET['export']).first()
            if et is None:
                raise Http404
            queryset = self.filter_queryset(self.get_queryset())
            return et.render_to_response(queryset)

        return super().list(request, *args, **kwargs)


class SequentialBulkCreatesMixin:
    """
    Perform bulk creation of new objects sequentially, rather than all at once. This ensures that any validation
    which depends on the evaluation of existing objects (such as checking for free space within a rack) functions
    appropriately.
    """
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            # Creating a single object
            return super().create(request, *args, **kwargs)

        return_data = []
        for data in request.data:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return_data.append(serializer.data)

        headers = self.get_success_headers(serializer.data)

        return Response(return_data, status=status.HTTP_201_CREATED, headers=headers)


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
    def get_bulk_update_queryset(self):
        return self.get_queryset()

    def bulk_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_bulk_update_queryset().filter(
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
    def get_bulk_destroy_queryset(self):
        return self.get_queryset()

    def bulk_destroy(self, request, *args, **kwargs):
        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        qs = self.get_bulk_destroy_queryset().filter(
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
