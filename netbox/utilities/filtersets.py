from netbox.registry import registry

__all__ = (
    'register_filterset',
)


def register_filterset(filterset_class):
    """
    Decorator for registering a FilterSet with the application registry.

    Uses model identifier as key to match search index pattern.
    """
    model = filterset_class._meta.model
    label = f'{model._meta.app_label}.{model._meta.model_name}'
    registry['filtersets'][label] = filterset_class
    return filterset_class
