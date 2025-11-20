from .constants import *
from .forms import *
from .mixins import *
from .utils import *


def register_filterset(filterset_class):
    """
    Decorator for registering a FilterSet with the application registry.

    Uses model identifier as key to match search index pattern.
    """
    def decorator(form_class):
        from netbox.registry import registry
        model = filterset_class._meta.model
        key = f'{model._meta.app_label}.{model._meta.model_name}'
        registry['filtersets'][key] = filterset_class
        return form_class
    return decorator
