from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


def get_permission_for_model(model, action):
    """
    Resolve the named permission for a given model (or instance) and action (e.g. view or add).

    :param model: A model or instance
    :param action: View, add, change, or delete (string)
    """
    if action not in ('view', 'add', 'change', 'delete'):
        raise ValueError(f"Unsupported action: {action}")

    return '{}.{}_{}'.format(
        model._meta.app_label,
        action,
        model._meta.model_name
    )


def resolve_permission(name):
    """
    Given a permission name, return the relevant ContentType and action. For example, "dcim.view_site" returns
    (Site, "view").

    :param name: Permission name in the format <app>.<action>_<model>
    """
    app_label, codename = name.split('.')
    action, model_name = codename.split('_')
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        raise ValueError(f"Unknown app/model for {name}")

    return content_type, action


def restrict_queryset(queryset, user, permission_required):
    """
    Filters a QuerySet to return only the objects on which the specified user has been granted the specified
    permission.

    :param queryset: Base QuerySet to be restricted
    :param user: User instance
    :param permission_required: Name of the required permission (e.g. "dcim.view_site")
    """
    obj_perm_attrs = user._object_perm_cache[permission_required]
    attrs = Q()
    for perm_attrs in obj_perm_attrs:
        if perm_attrs:
            attrs |= Q(**perm_attrs)
    return queryset.filter(attrs)
