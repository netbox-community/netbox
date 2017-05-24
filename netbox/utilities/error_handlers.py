from __future__ import unicode_literals

from django.contrib import messages
from django.utils.html import escape
from django.utils.safestring import mark_safe


def handle_protectederror(obj, request, e):
    """
    Generate a user-friendly error message in response to a ProtectedError exception.
    """
    try:
        dep_class = e.protected_objects[0]._meta.verbose_name_plural
    except IndexError:
        raise e

    # Grammar for single versus multiple triggering objects
    if type(obj) in (list, tuple):
        err_message = "Unable to delete the requested {}. The following dependent {} were found: ".format(
            obj[0]._meta.verbose_name_plural,
            dep_class,
        )
    else:
        err_message = "Unable to delete {} {}. The following dependent {} were found: ".format(
            obj._meta.verbose_name,
            obj,
            dep_class,
        )

    # Append dependent objects to error message
    dependent_objects = []
    for obj in e.protected_objects:
        if hasattr(obj, 'get_absolute_url'):
            dependent_objects.append('<a href="{}">{}</a>'.format(obj.get_absolute_url(), escape(obj)))
        else:
            dependent_objects.append(str(obj))
    err_message += ', '.join(dependent_objects)

    messages.error(request, mark_safe(err_message))
