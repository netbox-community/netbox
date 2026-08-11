import warnings
from collections import Counter
from contextlib import contextmanager

from django.core.exceptions import ObjectDoesNotExist
from django.db import router, transaction
from django.db.models import ProtectedError, RestrictedError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings

from core.models import ObjectType
from core.signals import clear_events
from extras.models import ExportTemplate
from netbox.api.serializers import BulkOperationSerializer
from netbox.api.serializers.bulk import get_bulk_update_serializer_class
from netbox.jobs import AsyncAPIJob
from utilities.exceptions import AbortRequest, RQWorkerNotRunningException
from utilities.request import copy_safe_request
from utilities.rqworker import any_workers_for_queue

__all__ = (
    'BackgroundOperationMixin',
    'BulkCreateModelMixin',
    'BulkDestroyModelMixin',
    'BulkUpdateModelMixin',
    'CustomFieldsMixin',
    'ExportTemplatesMixin',
    'ObjectValidationMixin',
    'SequentialBulkCreatesMixin',
    'discard_events_on_rollback',
    'get_duplicate_objects_response',
    'get_invalid_entries_response',
    'get_missing_objects_response',
    'get_non_list_response',
)


def get_non_list_response(data):
    """
    Return an error Response if the given request body is not a list of objects, or None if it is.

    A bulk operation always addresses a list. The body reaching one is not necessarily a list,
    however, as the router maps every PUT, PATCH, and DELETE on a list endpoint to a bulk action
    regardless of what was sent. Rejecting a non-list body here keeps the per-entry errors reported
    by the bulk actions correlated by position: those come from a serializer bound to a list, so
    they are only positional if the body was a list to begin with.

    The response carries only a `detail`, with no `errors`, as there are no entries to report
    against.
    """
    if isinstance(data, list):
        return None

    return Response(
        {
            'detail': _('Expected a list of objects, but got {datatype}.').format(
                datatype=type(data).__name__
            ),
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def get_invalid_entries_response(entry_errors):
    """
    Return a structured error Response for the entries of a bulk request which could not be
    interpreted, or None if every entry was interpretable.

    The bulk update and delete actions first check that each entry identifies an object, before any
    entry has been matched to one. A failure at that stage -- a missing or non-numeric `id`, or an
    entry which is not an object at all -- is reported against the entry's position in the request
    rather than against an object ID, since no object has been identified yet. This is the same
    correlation bulk create uses throughout, for the same reason.

    Passing this stage is what allows every later error to be correlated by `id` instead.

    :param entry_errors: The `errors` of a BulkOperationSerializer bound to a list, which holds one
        entry per object in the request (an empty dict where that object was interpretable).
    """
    errors = [
        {'index': i, 'errors': item_errors}
        for i, item_errors in enumerate(entry_errors)
        if item_errors
    ]
    if not errors:
        return None

    return Response(
        {
            'detail': _('{failed_count} of {total} objects failed validation.').format(
                failed_count=len(errors),
                total=len(entry_errors),
            ),
            'errors': errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def get_duplicate_objects_response(object_ids):
    """
    Return a structured error Response naming each of the given object IDs which appears more than
    once, or None if they are all distinct.

    A bulk operation identifies its objects by ID, so listing one twice is ambiguous. For an update,
    only one of the two sets of attributes can be applied, and the discarded entry is never even
    validated: a request pairing an invalid entry with a valid one for the same object would
    otherwise report success while silently ignoring the invalid data. For a delete, the repetition
    is meaningless, but it likewise causes the response to report on fewer objects than were named.
    Rather than guess at the intent, such a request is rejected.
    """
    errors = [
        {
            'id': object_id,
            'errors': {
                'id': [
                    _("Each object may be specified only once; ID {id} is listed {count} times").format(
                        id=object_id, count=count
                    ),
                ],
            },
        }
        # Counter preserves the order in which each ID was first seen
        for object_id, count in Counter(object_ids).items()
        if count > 1
    ]
    if not errors:
        return None

    return Response(
        {
            'detail': _('{failed_count} of {total} objects are listed more than once.').format(
                failed_count=len(errors),
                total=len(object_ids),
            ),
            'errors': errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def get_missing_objects_response(object_ids, queryset):
    """
    Return a structured error Response naming each of the given object IDs which the queryset does
    not match, or None if it matches them all.

    An ID goes unmatched either because no such object exists or because the requesting user's
    object-level permissions exclude it. The two are deliberately not distinguished, consistent with
    the single-object endpoints, which return a 404 in both cases.

    Bulk operations call this before performing any work: an unresolvable ID means the request names
    an object the client cannot act on, so there is nothing to be gained by attempting the batch (it
    would only be rolled back). Note that the status is 400 rather than the 409 a bulk delete
    returns for a dependency conflict, as this is a problem with the request itself rather than with
    the current state of the database.
    """
    found_pks = set(queryset.values_list('pk', flat=True))

    errors = [
        {
            'id': object_id,
            'errors': {
                'id': [_("Object with ID {id} does not exist").format(id=object_id)],
            },
        }
        # NetBox's bulk actions reject a repeated ID before reaching this point (see
        # get_duplicate_objects_response), but de-duplicate anyway so that any other caller reports
        # such an ID once rather than once per occurrence. dict.fromkeys() preserves the order of
        # first appearance.
        for object_id in dict.fromkeys(object_ids)
        if object_id not in found_pks
    ]
    if not errors:
        return None

    return Response(
        {
            'detail': _('{failed_count} of {total} objects could not be found.').format(
                failed_count=len(errors),
                total=len(object_ids),
            ),
            'errors': errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@contextmanager
def discard_events_on_rollback(sender, using=None):
    """
    Discard any queued events if the transaction wrapping this block is rolled back.

    The change logging signal receivers queue events eagerly, as the payload for a deleted object
    must be captured while that object and its related rows are still reachable. The queue is not
    flushed to the events pipeline until after the response has been rendered, however, so events
    queued for writes which were subsequently rolled back would otherwise still be dispatched,
    firing webhooks and event rules for changes that were never committed.

    Bulk operations need this because they provisionally write every valid object in a batch and
    then roll the entire batch back if any one object failed. Single-object writes need it because
    a write can be undone after it has been saved (for instance by the object-level permission
    check in perform_create()/perform_update(), or by a signal receiver raising AbortRequest). The
    UI's views send the same signal when they abandon a transaction.

    Must be entered *inside* the transaction whose rollback it guards, so that the rollback flag is
    still set when this block exits. Nesting is safe: the bulk actions guard the whole batch while
    the per-object perform_*() calls they make guard each write, and clearing an already-empty
    queue is a no-op.
    """
    try:
        yield
    except Exception:
        # An exception escaping the block (e.g. AbortRequest raised by a signal receiver) rolls
        # the transaction back just as an explicit set_rollback() does.
        clear_events.send(sender=sender)
        raise
    if transaction.get_connection(using).needs_rollback:
        clear_events.send(sender=sender)


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


class BulkCreateModelMixin:
    """
    Support the creation of multiple objects using the list endpoint for a model. Accepts a POST action with a list
    of one or more JSON objects, each specifying the attributes of an object to be created. For example:

    POST /api/dcim/sites/
    [
        {"name": "Site 1", "slug": "site-1"},
        {"name": "Site 2", "slug": "site-2"}
    ]
    """
    def bulk_create(self, request, *args, **kwargs):
        created_pks, errors = self.perform_bulk_create(request.data)

        if errors:
            return Response(
                {
                    'detail': _('{failed_count} of {total} objects failed validation.').format(
                        failed_count=len(errors),
                        total=len(request.data),
                    ),
                    'errors': errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Re-fetch the new objects to serialize them with their related objects prefetched. Order by PK
        # to ensure that the ordering of objects in the response matches the ordering of those in the
        # request (the objects were created in the order given, so PK order is request order).
        qs = self.get_queryset().filter(pk__in=created_pks).order_by('pk')
        serializer = self.get_serializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, data):
        created_pks = []
        errors = []
        using = router.db_for_write(self.queryset.model)
        with transaction.atomic(using=using), discard_events_on_rollback(self, using=using):
            # Validate and save each object in turn, rather than validating the entire batch up front,
            # so that validation which depends on the state left by prior saves is evaluated correctly.
            # This covers both validation against other existing objects (e.g. checking for free space
            # within a rack) and uniqueness: two objects in one batch which conflict with one another
            # would otherwise both validate against the pre-batch state and then fail on save, raising
            # an unhandled IntegrityError.
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    # Checked explicitly because get_serializer() infers many=True from a list, so a
                    # nested list would otherwise be validated as a batch of its own
                    errors.append({
                        'index': i,
                        'errors': {
                            api_settings.NON_FIELD_ERRORS_KEY: [
                                _('Invalid data. Expected a dictionary, but got {datatype}.').format(
                                    datatype=type(item).__name__
                                ),
                            ],
                        },
                    })
                    continue
                serializer = self.get_serializer(data=item)
                if not serializer.is_valid():
                    errors.append({'index': i, 'errors': serializer.errors})
                    continue
                try:
                    # Provisionally create even when a prior item failed, so subsequent
                    # cross-object validators see a realistic state. All creates are rolled
                    # back together if any item in the batch fails.
                    self.perform_create(serializer)
                except AbortRequest as e:
                    # Raised by a signal receiver rather than by validation (e.g. assigning a tag
                    # which is restricted to other object types). perform_create() wraps its write
                    # in its own atomic block, so the connection is rolled back to that savepoint
                    # and the remaining objects in the batch can still be evaluated. The message is
                    # coerced to a string because a few receivers pass an exception rather than text.
                    errors.append({'index': i, 'errors': {'__all__': [str(e.message)]}})
                else:
                    created_pks.append(serializer.instance.pk)
            if errors:
                transaction.set_rollback(True)
        return created_pks, errors


# TODO: Remove this in NetBox v5.0
class SequentialBulkCreatesMixin:
    """
    Deprecated no-op mixin retained for backward compatibility.

    Historically this was applied to individual ViewSets to make their bulk creates run one object
    at a time. All ViewSets derived from NetBoxModelViewSet now do this unconditionally (see
    BulkCreateModelMixin), so this mixin is a transparent pass-through and may be removed in a
    future release. Plugins should stop inheriting from it.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        warnings.warn(
            "SequentialBulkCreatesMixin is deprecated and no longer does anything; all bulk "
            f"creates are now performed sequentially. Remove it from {cls.__name__}.",
            DeprecationWarning,
            stacklevel=2,
        )


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

        if (response := get_non_list_response(request.data)) is not None:
            return response

        # Check that every entry identifies an object before matching any of them to one, so that
        # a malformed entry is reported in the same form as every other bulk error
        serializer = BulkOperationSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return get_invalid_entries_response(serializer.errors)

        object_ids = [o['id'] for o in serializer.validated_data]

        # Reject the batch if any object is named more than once, rather than applying only one of
        # the entries given for it.
        if (response := get_duplicate_objects_response(object_ids)) is not None:
            return response

        qs = self.get_bulk_update_queryset().filter(pk__in=object_ids)

        # Reject the batch if any of the objects to be updated could not be found, rather than
        # silently omitting them from the response.
        if (response := get_missing_objects_response(object_ids, qs)) is not None:
            return response

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
        using = router.db_for_write(self.queryset.model)
        with transaction.atomic(using=using), discard_events_on_rollback(self, using=using):
            # Validate and save each object in turn so subsequent validations see the DB
            # state left by prior saves (e.g. two items renamed to the same name: the second
            # will fail validation rather than raising an integrity error on save).
            for obj in objects:
                data = update_data.get(obj.id)
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                serializer = self.get_serializer(obj, data=data, partial=partial)
                if not serializer.is_valid():
                    errors.append({'id': obj.pk, 'errors': serializer.errors})
                    continue
                try:
                    self.perform_update(serializer)
                except AbortRequest as e:
                    # Raised by a signal receiver rather than by validation (e.g. assigning a tag
                    # which is restricted to other object types). perform_update() wraps its write
                    # in its own atomic block, so the connection is rolled back to that savepoint
                    # and the remaining objects in the batch can still be evaluated. The message is
                    # coerced to a string because a few receivers pass an exception rather than text.
                    errors.append({'id': obj.pk, 'errors': {'__all__': [str(e.message)]}})
                else:
                    updated_pks.append(obj.pk)
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

        if (response := get_non_list_response(request.data)) is not None:
            return response

        # Check that every entry identifies an object before matching any of them to one, so that
        # a malformed entry is reported in the same form as every other bulk error
        serializer = BulkOperationSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return get_invalid_entries_response(serializer.errors)

        object_ids = [o['id'] for o in serializer.validated_data]

        # Reject the batch if any object is named more than once, rather than ignoring the
        # repetition (and any changelog message attached to it) and reporting success.
        if (response := get_duplicate_objects_response(object_ids)) is not None:
            return response

        qs = self.get_bulk_destroy_queryset().filter(pk__in=object_ids)

        # Reject the batch if any of the objects to be deleted could not be found, rather than
        # silently omitting them and reporting success.
        if (response := get_missing_objects_response(object_ids, qs)) is not None:
            return response

        # Compile any changelog messages to be recorded on the objects being deleted
        changelog_messages = {
            o['id']: o.get('changelog_message') for o in serializer.validated_data
        }

        errors, total, has_conflict = self.perform_bulk_destroy(qs, changelog_messages)

        if errors:
            # A dependency conflict reports 409, as it is a conflict with the current state of the
            # database; every other failure reports 400, as it is a rejection of the request. This
            # matches the single-object endpoint, where dispatch() maps the same two exception
            # classes to the same two status codes. Where a batch hit both, the conflict takes
            # precedence: it is the failure which would remain were the request itself corrected.
            return Response(
                {
                    'detail': _('{failed_count} of {total} objects could not be deleted.').format(
                        failed_count=len(errors),
                        total=total,
                    ),
                    'errors': errors,
                },
                status=status.HTTP_409_CONFLICT if has_conflict else status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, objects, changelog_messages=None):
        """
        Attempt to delete each of the given objects, rolling the entire batch back if any one of
        them could not be deleted.

        Returns the per-object errors, the number of objects processed, and whether any of the
        failures was a conflict with the current state of the database (a dependent object) rather
        than a rejection of the request (a protection rule, or any other signal receiver raising
        AbortRequest). The caller uses the last of these to select a status code.
        """
        changelog_messages = changelog_messages or {}
        errors = []
        total = 0
        has_conflict = False
        using = router.db_for_write(self.queryset.model)
        with transaction.atomic(using=using), discard_events_on_rollback(self, using=using):
            for obj in objects:
                total += 1
                if hasattr(obj, 'snapshot'):
                    obj.snapshot()
                obj._changelog_message = changelog_messages.get(obj.pk)
                pk = obj.pk  # Django sets obj.pk = None after deletion; capture it first
                try:
                    self.perform_destroy(obj)
                except (ProtectedError, RestrictedError) as e:
                    has_conflict = True
                    protected = list(
                        e.protected_objects if isinstance(e, ProtectedError) else e.restricted_objects
                    )
                    # Report only the count, not names or PKs, to keep each per-object error
                    # entry small in a batch response. Note: the single-object delete endpoint
                    # (NetBoxModelViewSet.dispatch()) does include names and PKs of dependent
                    # objects, so this is not a hard security boundary — just a narrower
                    # response shape for the bulk case.
                    errors.append({
                        'id': pk,
                        'errors': {
                            '__all__': [
                                _('Unable to delete: {n} dependent object(s) prevent deletion.').format(
                                    n=len(protected)
                                ),
                            ],
                        },
                    })
                except AbortRequest as e:
                    # Raised by a signal receiver rather than by a database constraint (e.g. a
                    # PROTECTION_RULES violation caught in core.signals.handle_deleted_object).
                    # perform_destroy() wraps its delete in its own atomic block, so the connection
                    # is rolled back to that savepoint and the remaining objects in the batch can
                    # still be evaluated.
                    errors.append({'id': pk, 'errors': {'__all__': [str(e.message)]}})
            if errors:
                transaction.set_rollback(True)
        return errors, total, has_conflict


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
