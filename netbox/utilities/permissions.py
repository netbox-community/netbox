from django.conf import settings
from django.contrib.contenttypes.models import ContentType


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


def get_permission_action(name):
    """
    Return the action component (e.g. view or add) from a permission name.

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    try:
        return name.split('.')[1].split('_')[0]
    except ValueError:
        raise ValueError(
            f"Invalid permission name: {name}. Must be in the format <app_label>.<action>_<model>"
        )


def resolve_permission(name):
    """
    Given a permission name, return the relevant ContentType and action. For example, "dcim.view_site" returns
    (Site, "view").

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    app_label, codename = name.split('.')
    action, model_name = codename.split('_')
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        raise ValueError(f"Unknown app/model for {name}")

    return content_type, action


def permission_is_exempt(name):
    """
    Determine whether a specified permission is exempt from evaluation.

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    app_label, codename = name.split('.')
    action, model_name = codename.split('_')

    if action == 'view':
        if (
            # All models are exempt from view permission enforcement
            '*' in settings.EXEMPT_VIEW_PERMISSIONS
        ) or (
            # This specific model is exempt from view permission enforcement
            '{}.{}'.format(app_label, model_name) in settings.EXEMPT_VIEW_PERMISSIONS
        ):
            return True

    return False
