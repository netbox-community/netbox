from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

__all__ = (
    'get_permission_for_model',
    'permission_is_exempt',
    'qs_filter_from_constraints',
    'resolve_permission',
    'resolve_permission_ct',
)


def get_permission_for_model(model, action):
    """
    Resolve the named permission for a given model (or instance) and action (e.g. view or add).

    :param model: A model or instance
    :param action: View, add, change, or delete (string)
    """
    # Resolve to the "concrete" model (for proxy models)
    model = model._meta.concrete_model

    return f'{model._meta.app_label}.{action}_{model._meta.model_name}'


def resolve_permission(name):
    """
    Given a permission name, return the app_label, action, and model_name components. For example, "dcim.view_site"
    returns ("dcim", "view", "site").

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    try:
        app_label, codename = name.split('.')
        action, model_name = codename.rsplit('_', 1)
    except ValueError:
        raise ValueError(
            _("Invalid permission name: {name}. Must be in the format <app_label>.<action>_<model>").format(name=name)
        )

    return app_label, action, model_name


def resolve_permission_ct(name):
    """
    Given a permission name, return the relevant ContentType and action. For example, "dcim.view_site" returns
    (Site, "view").

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    from core.models import ObjectType
    app_label, action, model_name = resolve_permission(name)
    try:
        object_type = ObjectType.objects.get(app_label=app_label, model=model_name)
    except ObjectType.DoesNotExist:
        raise ValueError(_("Unknown app_label/model_name for {name}").format(name=name))

    return object_type, action


def permission_is_exempt(name):
    """
    Determine whether a specified permission is exempt from evaluation.

    :param name: Permission name in the format <app_label>.<action>_<model>
    """
    app_label, action, model_name = resolve_permission(name)

    if action == 'view':
        if (
            # All models (excluding those in EXEMPT_EXCLUDE_MODELS) are exempt from view permission enforcement
            '*' in settings.EXEMPT_VIEW_PERMISSIONS and (app_label, model_name) not in settings.EXEMPT_EXCLUDE_MODELS
        ) or (
            # This specific model is exempt from view permission enforcement
            f'{app_label}.{model_name}' in settings.EXEMPT_VIEW_PERMISSIONS
        ):
            return True

    return False


def qs_filter_from_constraints(constraints, tokens=None):
    """
    Construct a Q filter object from an iterable of ObjectPermission constraints.

    Args:
        tokens: A dictionary mapping string tokens to be replaced with a value.
    """
    if tokens is None:
        tokens = {}

    def _replace_tokens(value, tokens):
        if type(value) is list:
            return list(map(lambda v: tokens.get(v, v), value))
        return tokens.get(value, value)

    params = Q()
    for constraint in constraints:
        if constraint:
            params |= Q(**{k: _replace_tokens(v, tokens) for k, v in constraint.items()})
        else:
            # Found null constraint; permit model-level access
            return Q()

    return params
