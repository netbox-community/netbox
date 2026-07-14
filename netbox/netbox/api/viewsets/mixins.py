from django.core.exceptions import ObjectDoesNotExist
from django.db import router, transaction
from django.db.models import ProtectedError, RestrictedError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from core.models import ObjectType
from extras.models import ExportTemplate
from netbox.api.serializers import BulkOperationSerializer
from netbox.api.serializers.bulk import get_bulk_update_serializer_class
from netbox.jobs import AsyncAPIJob
from utilities.exceptions import RQWorkerNotRunningException
from utilities.request import copy_safe_request
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
    request to a list endpoint includes ``?background=true``, the bulk action enqueues an
    ``AsyncAPIJob`` to perform the work and immediately returns ``202 Accepted`` with the
    job's ID and polling URL. The actual write (including validation) runs in a worker via
    the same action method, so behavior is identical to the synchronous path.

    This mixin overrides no framework methods; the bulk action methods call its helpers.
    """

    def _background_requested(self, request):
        """Return True if background processing was requested for this write."""
        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return False
        return request.query_params.get('background', '').lower() == 'true'

    def _handle_background_request(self, request, action, action_kwargs=None):
        """
        Shared entry point for the bulk write actions. If background processing was requested
        for a bulk (list) operation, enqueue an AsyncAPIJob and return a 202 Response; otherwise
        return None so the caller proceeds synchronously.

        Validation is intentionally deferred to the worker (which runs the same action method),
        so it is not performed twice and the request returns promptly regardless of batch size.
        """
        if not (isinstance(request.data, list) and self._background_requested(request)):
            return None

        return self._enqueue_bulk_job(request, action, payload=list(request.data), action_kwargs=action_kwargs)

    def _enqueue_bulk_job(self, request, action, payload, action_kwargs=None):
        """
        Enqueue an AsyncAPIJob to perform the given bulk action in the background and return
        a 202 response containing the job ID and polling URL.
        """
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
        # Carry a serializable snapshot of the request so the worker can reconstruct it (method,
        # request ID, and host metadata for absolute URLs in the captured result). The scheme is
        # passed separately, as copy_safe_request() does not capture it. The worker re-fetches the
        # user by PK and bypasses authentication entirely, so it reads neither the copied user nor
        # cookies; drop both so no User instance or session data is pickled into the job payload
        # for the lifetime of the job.
        request_copy = copy_safe_request(request, include_files=False)
        request_copy.user = None
        request_copy.COOKIES = {}

        job = AsyncAPIJob.enqueue(
            name=job_name,
            user=request.user,
            viewset_class=f'{type(self).__module__}.{type(self).__qualname__}',
            action=action,
            payload=payload,
            user_pk=request.user.pk,
            action_kwargs=action_kwargs or {},
            request=request_copy,
            scheme=request.scheme,
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
        # If background processing was requested for a bulk (list) create, enqueue a job and
        # return immediately. _handle_background_request() comes from BackgroundOperationMixin;
        # fall back to "no background" so this mixin remains usable on its own (e.g. in custom
        # viewsets).
        handle_background = getattr(self, '_handle_background_request', lambda *a, **kw: None)
        if (response := handle_background(request, 'create')) is not None:
            return response

        # Create objects sequentially so each validation sees the state left by prior creates
        # (e.g. rack space checks). Collect per-object errors instead of failing on the first.
        errors = []
        return_data = []
        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
            if not isinstance(request.data, list):
                # Creating a single object
                return super().create(request, *args, **kwargs)

            total = len(request.data)
            for i, data in enumerate(request.data):
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    # Provisionally create even when a prior item failed, so subsequent
                    # cross-object validators (e.g. rack space checks) see a realistic state.
                    # All creates are rolled back together if any item in the batch fails.
                    self.perform_create(serializer)
                    return_data.append(serializer.data)
                else:
                    errors.append({'index': i, 'errors': serializer.errors})

            if errors:
                transaction.set_rollback(True)

        if errors:
            return Response(
                {
                    'detail': _('{failed_count} of {total} objects failed validation.').format(
                        failed_count=len(errors),
                        total=total,
                    ),
                    'errors': errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = self.get_success_headers(return_data[-1]) if return_data else {}
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

        # If background processing was requested, enqueue a job and return immediately (before
        # any validation, which is deferred to the worker). _handle_background_request() comes
        # from BackgroundOperationMixin; fall back to "no background" so this mixin remains
        # usable on its own (e.g. in custom viewsets).
        handle_background = getattr(self, '_handle_background_request', lambda *a, **kw: None)
        action = 'bulk_partial_update' if partial else 'bulk_update'
        if (response := handle_background(request, action)) is not None:
            return response

        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        qs = self.get_bulk_update_queryset().filter(
            pk__in=[o['id'] for o in serializer.data]
        )

        # Map update data by object ID
        update_data = {
            obj.pop('id'): obj for obj in request.data
        }

        object_pks, errors = self.perform_bulk_update(qs, update_data, partial=partial)

        if errors:
            return Response(
                {
                    'detail': _('{failed_count} of {total} objects failed validation.').format(
                        failed_count=len(errors),
                        total=len(object_pks) + len(errors),
                    ),
                    'errors': errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prefetch related objects for all updated instances
        qs = self.get_queryset().filter(pk__in=object_pks)
        serializer = self.get_serializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_bulk_update(self, objects, update_data, partial):
        updated_pks = []
        errors = []
        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
            # Validate and save each object in turn so subsequent validations see the DB
            # state left by prior saves (e.g. two items renamed to the same name: the second
            # will fail validation rather than raising an integrity error on save).
            for obj in objects:
                data = update_data.get(obj.id)
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                serializer = self.get_serializer(obj, data=data, partial=partial)
                if serializer.is_valid():
                    self.perform_update(serializer)
                    updated_pks.append(obj.pk)
                else:
                    errors.append({'id': obj.pk, 'errors': serializer.errors})
            if errors:
                transaction.set_rollback(True)
        return updated_pks, errors

    def get_bulk_update_serializer_class(self, *, partial=False):
        return get_bulk_update_serializer_class(
                self.get_serializer_class(),
                partial=partial,
            )

    def get_bulk_update_request_serializer(self, *, partial=False):
        serializer_class = self.get_bulk_update_serializer_class(partial=partial)

        # Important: do NOT pass partial=True here. The partial schema class already
        # makes non-id fields optional, and passing partial=True would also make id
        # appear optional in OpenAPI.
        return serializer_class(many=True)

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
        # If background processing was requested, enqueue a job and return immediately (before
        # any validation, which is deferred to the worker). _handle_background_request() comes
        # from BackgroundOperationMixin; fall back to "no background" so this mixin remains
        # usable on its own (e.g. in custom viewsets).
        handle_background = getattr(self, '_handle_background_request', lambda *a, **kw: None)
        if (response := handle_background(request, 'bulk_destroy')) is not None:
            return response

        serializer = BulkOperationSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        qs = self.get_bulk_destroy_queryset().filter(
            pk__in=[o['id'] for o in serializer.validated_data]
        )

        # Compile any changelog messages to be recorded on the objects being deleted
        changelog_messages = {
            o['id']: o.get('changelog_message') for o in serializer.validated_data
        }

        errors, total = self.perform_bulk_destroy(qs, changelog_messages)

        if errors:
            return Response(
                {
                    'detail': _('{failed_count} of {total} objects could not be deleted.').format(
                        failed_count=len(errors),
                        total=total,
                    ),
                    'errors': errors,
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, objects, changelog_messages=None):
        changelog_messages = changelog_messages or {}
        errors = []
        total = 0
        with transaction.atomic(using=router.db_for_write(self.queryset.model)):
            for obj in objects:
                total += 1
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                obj._changelog_message = changelog_messages.get(obj.pk)
                pk = obj.pk  # Django sets obj.pk = None after deletion; capture it first
                try:
                    self.perform_destroy(obj)
                except (ProtectedError, RestrictedError) as e:
                    protected = list(
                        e.protected_objects if isinstance(e, ProtectedError) else e.restricted_objects
                    )
                    n = len(protected)
                    # Report only the count, not names or PKs, to keep each per-object error
                    # entry small in a batch response. Note: the single-object delete endpoint
                    # (NetBoxModelViewSet.dispatch()) does include names and PKs of dependent
                    # objects, so this is not a hard security boundary — just a narrower
                    # response shape for the bulk case.
                    errors.append({
                        'id': pk,
                        'errors': {
                            '__all__': _(
                                'Unable to delete: {n} dependent object(s) prevent deletion.'
                            ).format(n=n),
                        },
                    })
            if errors:
                transaction.set_rollback(True)
        return errors, total


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
