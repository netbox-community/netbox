from django.contrib import messages
from django.db.models import ProtectedError, RestrictedError
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def handle_protectederror(obj_list, request, e):
    """
    Generate a user-friendly error message in response to a ProtectedError or RestrictedError exception.
    """
    if type(e) is ProtectedError:
        protected_objects = list(e.protected_objects)
    elif type(e) is RestrictedError:
        protected_objects = list(e.restricted_objects)
    else:
        raise e

    # Formulate the error message
    err_message = _("Unable to delete <strong>{objects}</strong>. {count} dependent objects were found: ").format(
        objects=', '.join(str(obj) for obj in obj_list),
        count=len(protected_objects) if len(protected_objects) <= 50 else _('More than 50')
    )

    # Append dependent objects to error message
    dependent_objects = []
    for dependent in protected_objects[:50]:
        if hasattr(dependent, 'get_absolute_url'):
            dependent_objects.append(f'<a href="{dependent.get_absolute_url()}">{escape(dependent)}</a>')
        else:
            dependent_objects.append(str(dependent))
    err_message += ', '.join(dependent_objects)

    messages.error(request, mark_safe(err_message))
