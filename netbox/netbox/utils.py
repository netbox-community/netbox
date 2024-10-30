from netbox.registry import registry

__all__ = (
    'get_data_backend_choices',
    'register_data_backend',
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
