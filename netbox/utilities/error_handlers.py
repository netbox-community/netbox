from django.contrib import messages


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
        err_message = u"Unable to delete the requested {}. The following dependent {} were found: ".format(
            obj[0]._meta.verbose_name_plural,
            dep_class,
        )
    else:
        err_message = u"Unable to delete {} {}. The following dependent {} were found: ".format(
            obj._meta.verbose_name,
            obj,
            dep_class,
        )

    # Append dependent objects to error message
    dependent_objects = []
    for o in e.protected_objects:
        if hasattr(o, 'get_absolute_url'):
            dependent_objects.append(u'<a href="{}">{}</a>'.format(o.get_absolute_url(), o))
        else:
            dependent_objects.append(str(o))
    err_message += u', '.join(dependent_objects)

    messages.error(request, err_message)
