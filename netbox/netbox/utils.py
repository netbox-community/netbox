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


def convert_byte_size(value, unit="mega"):
    """
    Convert a size value to unit.
    """
    factors = {
        "kilo": 1024,
        "mega": 1024 ** 2,
        "giga": 1024 ** 3,
        "tera": 1024 ** 4,
    }
    if value:
        if len(str(value)) < 6:
            return value
        value_converted = float(value) / factors[unit]
        return value_converted
    return 0
