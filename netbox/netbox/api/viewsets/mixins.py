from django.core.exceptions import ObjectDoesNotExist
from django.db import router, transaction
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from core.models import ObjectType
from extras.models import ExportTemplate
from netbox.api.serializers import BulkOperationSerializer
from utilities.exceptions import RQWorkerNotRunningException
from utilities.rqworker import any_workers_for_queue

__all__ = (
    'BackgroundOperationMixin',
    'BulkDestroyModelMixin',
    'BulkUpdateModelMixin',
    'CustomFieldsMixin',
    'ExportTemplatesMixin',
    'ObjectValidationMixin',
    'SequentialBulkCreatesMixin',
)


class BackgroundOperationMixin:
    """
    Enable optional background processing of REST API bulk write operations. When a write
    request to a list endpoint includes ``?background=true``, the bulk action validates the
    payload synchronously, enqueues an ``AsyncAPIJob`` to perform the work, and immediately
    returns ``202 Accepted`` with the job's ID and polling URL. The actual write runs in a
    worker via the same action method, so behavior is identical to the synchronous path.

    This mixin overrides no framework methods; the bulk action methods call its helpers.
    """

    def _background_requested(self, request):
        """Return True if background processing was requested for this write."""
        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return False
        return request.query_params.get('background', '').lower() == 'true'

    def _maybe_background_bulk_create(self, request):
        """
        Shared entry point for the create() overrides. If background processing was requested
        for a bulk (list) create, validate the payload synchronously and return a 202 Response;
        otherwise return None so the caller proceeds with synchronous creation.
        """
        if not (isinstance(request.data, list) and self._background_requested(request)):
            return None

        # Validate synchronously before enqueuing so a malformed payload is rejected with a
        # 400 now, rather than producing a 202 for work that can never succeed. (Constraints
        # that depend on other items in the batch are still evaluated when the job runs.)
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        return self._enqueue_bulk_job(request, 'create', payload=list(request.data))

    def _enqueue_bulk_job(self, request, action, payload, action_kwargs=None):
        """
        Enqueue an AsyncAPIJob to perform the given bulk action in the background and return
        a 202 response containing the job ID and polling URL.
        """
        from netbox.jobs import AsyncAPIJob

        # Reject conditional requests: an If-Match precondition cannot be meaningfully
        # honored when the write is deferred to a worker (the TOCTOU window is unbounded).
        if request.META.get('HTTP_IF_MATCH'):
            raise ValidationError(
                _("The If-Match header is not supported with background processing.")
            )

        # Don't accept work that no worker can perform (mirrors the scripts API; AsyncAPIJob
        # is enqueued without an instance, so it always lands on the default queue).
        if not any_workers_for_queue('default'):
            raise RQWorkerNotRunningException()

        model = self.queryset.model
        verb = _("delete") if action == 'bulk_destroy' else (
            _("create") if action == 'create' else _("update")
        )
        job_name = _("Bulk {verb} {object_type}").format(
            verb=verb,
            object_type=model._meta.verbose_name_plural,
        )
        job = AsyncAPIJob.enqueue(
            name=job_name,
            user=request.user,
            viewset_class=f'{type(self).__module__}.{type(self).__qualname__}',
            action=action,
            payload=payload,
            user_pk=request.user.pk,
            request_id=str(getattr(request, 'id', '')),
            method=request.method,
            action_kwargs=action_kwargs or {},
        )

        job_url = reverse('core-api:job-detail', kwargs={'pk': job.pk}, request=request)
        response = Response(
            {'job': {'id': job.pk, 'url': job_url, 'status': job.status}},
            status=status.HTTP_202_ACCEPTED,
        )
        response['Location'] = job_url
        return response


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
            et = ExportTemplate.objects.restrict(request.user, 'view').filter(
                object_types=object_type,
                name=request.GET['export'],
            ).first()
            if et is None:
                raise Http404
            queryset = self.filter_queryset(self.get_queryset())
            return et.render_to_response(queryset=queryset)

        return super().list(request, *args, **kwargs)


class SequentialBulkCreatesMixin:
    """
    Perform bulk creation of new objects sequentially, rather than all at once. This ensures that any validation
    which depends on the evaluation of existing objects (such as checking for free space within a rack) functions
    appropriately.
    """
    def create(self, request, *args, **kwargs):
        # If background processing was requested for a bulk (list) create, validate and enqueue.
        if (response := self._maybe_background_bulk_create(request)) is not None:
            return response

        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
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

        # If background processing was requested, enqueue a job and return immediately.
        # The payload is captured here, before the request.data mutation below.
        if self._background_requested(request):
            action = 'bulk_partial_update' if partial else 'bulk_update'
            return self._enqueue_bulk_job(request, action, payload=list(request.data))

        qs = self.get_bulk_update_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        # Map update data by object ID
        update_data = {
            obj.pop('id'): obj for obj in request.data
        }

        object_pks = self.perform_bulk_update(qs, update_data, partial=partial)

        # Prefetch related objects for all updated instances
        qs = self.get_queryset().filter(pk__in=object_pks)
        serializer = self.get_serializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_bulk_update(self, objects, update_data, partial):
        updated_pks = []
        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
            for obj in objects:
                data = update_data.get(obj.id)
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                serializer = self.get_serializer(obj, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                updated_pks.append(obj.pk)

        return updated_pks

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

        # If background processing was requested, enqueue a job and return immediately.
        if self._background_requested(request):
            return self._enqueue_bulk_job(request, 'bulk_destroy', payload=list(request.data))

        qs = self.get_bulk_destroy_queryset().filter(
            pk__in=[o['id'] for o in serializer.validated_data]
        )

        # Compile any changelog messages to be recorded on the objects being deleted
        changelog_messages = {
            o['id']: o.get('changelog_message') for o in serializer.validated_data
        }

        self.perform_bulk_destroy(qs, changelog_messages)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, objects, changelog_messages=None):
        changelog_messages = changelog_messages or {}
        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
            for obj in objects:
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                obj._changelog_message = changelog_messages.get(obj.pk)
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
