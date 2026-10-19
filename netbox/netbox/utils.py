from netbox.registry import registry
from utilities.choices import Choice

__all__ = (
    'allocate_pks',
    'get_data_backend_choices',
    'register_data_backend',
    'register_model_feature',
    'register_pk_allocator',
    'register_request_processor',
)


def get_data_backend_choices():
    return [
        (None, '---------'),
        *[
            Choice(name, cls.label) for name, cls in registry['data_backends'].items()
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


def register_pk_allocator(func):
    """
    Decorator for registering a primary key allocator: a callable which may supply primary keys for new objects.

    The callable must accept a model class and a count, and return either a list of exactly `count` primary keys for
    that model, or None to defer to the next allocator (and ultimately to the database). Allocators are consulted in
    the order in which they were registered.

        @register_pk_allocator
        def my_allocator(model, count):
            ...
    """
    registry['pk_allocators'].append(func)

    return func


def allocate_pks(model, count=1):
    """
    Return a list of `count` primary keys for new instances of `model` from the first registered allocator which
    supplies them, or None if the database should assign them. Code which inserts rows outside the ORM (e.g. using raw
    SQL or COPY) can call this to obtain primary keys in the same manner as Model.save() and QuerySet.bulk_create().
    """
    for allocator in registry['pk_allocators']:
        if (pks := allocator(model, count)) is not None:
            pks = list(pks)
            if len(pks) != count:
                name = getattr(allocator, '__qualname__', allocator)
                raise ValueError(
                    f"Primary key allocator {name} returned {len(pks)} primary keys for {model._meta.label} "
                    f"(expected {count})."
                )
            return pks
    return None
