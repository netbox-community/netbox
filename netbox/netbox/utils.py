import warnings
from importlib import import_module

from netbox.registry import registry

__all__ = (
    'register_model_feature',
)

# Functions which have been relocated from this module, mapped to their new modules
# TODO: Remove in NetBox v5.0
RELOCATED_FUNCTIONS = {
    'get_data_backend_choices': 'netbox.data_backends',
    'register_data_backend': 'netbox.data_backends',
    'register_request_processor': 'utilities.request',
}


def __getattr__(name):
    if module := RELOCATED_FUNCTIONS.get(name):
        warnings.warn(
            f"Importing {name}() from netbox.utils is deprecated and will be removed in NetBox v5.0. Import it from "
            f"{module} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(import_module(module), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def register_model_feature(name, func=None):
    """
    Register a model feature with its qualifying function.

    The qualifying function must accept a single `model` argument. It will be called to determine whether the given
    model supports the corresponding feature.

    This function can be used directly:

        register_model_feature('my_feature', my_func)

    Or as a decorator:

        @register_model_feature('my_feature')
        def my_func(model):
            ...
    """
    def decorator(f):
        registry['model_features'][name] = f
        return f

    if name in registry['model_features']:
        raise ValueError(f"A model feature named {name} is already registered.")

    if func is None:
        return decorator
    return decorator(func)
