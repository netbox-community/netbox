from django.contrib import messages
from django.utils.html import escape
from django.utils.safestring import mark_safe


def handle_protectederror(obj_list, request, e):
    """
    Generate a user-friendly error message in response to a ProtectedError exception.
    """
    protected_objects = list(e.protected_objects)
    protected_count = len(protected_objects) if len(protected_objects) <= 50 else 'More than 50'
    err_message = f"Unable to delete <strong>{', '.join(str(obj) for obj in obj_list)}</strong>. " \
                  f"{protected_count} dependent objects were found: "

    # Append dependent objects to error message
    dependent_objects = []
    for dependent in protected_objects[:50]:
        if hasattr(dependent, 'get_absolute_url'):
            dependent_objects.append(f'<a href="{dependent.get_absolute_url()}">{escape(dependent)}</a>')
        else:
            dependent_objects.append(str(dependent))
    err_message += ', '.join(dependent_objects)

    messages.error(request, mark_safe(err_message))
