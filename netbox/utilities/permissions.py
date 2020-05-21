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
