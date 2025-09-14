from netbox.registry import registry

__all__ = (
    'get_data_backend_choices',
    'register_data_backend',
    'register_model_feature',
    'register_request_processor',
)


def get_data_backend_choices():
    return [
        (None, '---------'),
        *[
            (name, cls.label) for name, cls in registry['data_backends'].items()
        ]
    ]


def register_data_backend():
    """
    Decorator for registering a DataBackend class.
    """
    def _wrapper(cls):
        registry['data_backends'][cls.name] = cls
        return cls

    return _wrapper


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


def register_request_processor(func):
    """
    Decorator for registering a request processor.
    """
    registry['request_processors'].append(func)

    return func
