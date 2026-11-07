import platform
import sys
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.db.models import ProtectedError, RestrictedError
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from rest_framework import status

__all__ = (
    'get_viewable_protected_objects',
    'handle_protectederror',
    'handle_rest_api_exception',
)


def get_viewable_protected_objects(e, user):
    """
    Return the dependent objects of a ProtectedError or RestrictedError which the user is permitted to view, and the
    number of those which they are not.
    """
    protected_objects = list(e.protected_objects if isinstance(e, ProtectedError) else e.restricted_objects)
    if user.is_active and user.is_superuser:
        return protected_objects, 0

    # Group the objects by the database from which each was loaded and by model
    pks_by_model = defaultdict(list)
    for obj in protected_objects:
        pks_by_model[(obj._state.db, obj._meta.model)].append(obj.pk)
    viewable_pks = defaultdict(set)
    for (using, model), pks in pks_by_model.items():
        queryset = model._default_manager.using(using)
        # Objects of a model which doesn't support restriction are treated as not viewable
        if hasattr(queryset, 'restrict'):
            viewable_pks[(using, model)] = set(
                queryset.restrict(user, 'view').filter(pk__in=pks).values_list('pk', flat=True)
            )

    viewable_objects = [
        obj for obj in protected_objects if obj.pk in viewable_pks[(obj._state.db, obj._meta.model)]
    ]
    return viewable_objects, len(protected_objects) - len(viewable_objects)


def handle_protectederror(obj_list, request, e):
    """
    Generate a user-friendly error message in response to a ProtectedError or RestrictedError exception.
    """
    if type(e) not in (ProtectedError, RestrictedError):
        raise e
    viewable_objects, hidden_count = get_viewable_protected_objects(e, request.user)

    # Formulate the error message
    err_message = _('Unable to delete <strong>{objects}</strong>. {count} dependent objects were found: ').format(
        objects=', '.join(escape(obj) for obj in obj_list),
        count=len(viewable_objects) + hidden_count,
    )

    # Append dependent objects to error message, naming only those which the user is permitted to view
    dependent_objects = []
    for dependent in viewable_objects[:50]:
        if hasattr(dependent, 'get_absolute_url'):
            dependent_objects.append(f'<a href="{dependent.get_absolute_url()}">{escape(dependent)}</a>')
        else:
            dependent_objects.append(escape(str(dependent)))
    if (more_count := len(viewable_objects) - 50) > 0:
        dependent_objects.append(escape(ngettext(
            '{count} more object',
            '{count} more objects',
            more_count,
        ).format(count=more_count)))
    if hidden_count:
        dependent_objects.append(escape(ngettext(
            '{count} object you do not have permission to view',
            '{count} objects you do not have permission to view',
            hidden_count,
        ).format(count=hidden_count)))
    err_message += ', '.join(dependent_objects)

    messages.error(request, mark_safe(err_message))


def handle_rest_api_exception(request, *args, **kwargs):
    """
    Handle exceptions and return a useful error message for REST API requests.
    """
    if 'error' in kwargs:
        error_message = str(kwargs['error'])
        type_, __ = sys.exc_info()[:2]
        exception_name = type_.__name__ if type_ else 'Exception'
    else:
        type_, error = sys.exc_info()[:2]
        error_message = str(error)
        exception_name = type_.__name__
    data = {
        'error': error_message,
        'exception': exception_name,
        'netbox_version': settings.RELEASE.full_version,
        'python_version': platform.python_version(),
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
