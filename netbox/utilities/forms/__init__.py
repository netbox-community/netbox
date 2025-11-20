from .constants import *
from .forms import *
from .mixins import *
from .utils import *


def register_filterset(filterset_class):
    """
    Decorator for registering a FilterForm -> FilterSet mapping.

    Usage:
        @register_filterset(DeviceFilterSet)
        class DeviceFilterForm(NetBoxModelFilterSetForm):
            ...

    Args:
        filterset_class: The corresponding filterset class
    """
    def decorator(form_class):
        from netbox.registry import registry
        registry['filtersets'][form_class] = filterset_class
        return form_class
    return decorator
