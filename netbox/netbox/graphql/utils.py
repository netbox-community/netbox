import logging

from netbox.registry import registry

__all__ = (
    'get_model_label',
    'register_model_graphql_type',
    'splice_extension_bases',
)


def get_model_label(model):
    """
    Return the canonical `app_label.model_name` label used to key GraphQL extensions in the registry. Both the
    registration side and the lookup side must derive labels through this helper so they always agree.
    """
    return f'{model._meta.app_label}.{model._meta.model_name}'


def _own_names(klass):
    """
    Return the set of field/attribute names a single class contributes directly: its annotations and its own
    non-dunder attributes (such as resolver methods), excluding the `models` extension marker.
    """
    names = set(getattr(klass, '__annotations__', {}))
    names |= {name for name in vars(klass) if not name.startswith('__')}
    names.discard('models')
    return names


def _core_names(cls):
    """
    Return every name `cls` resolves (its own body and everything it inherits). Extensions are spliced in *after*
    these bases, so any name already present here is provided by the core type and an extension cannot override it.
    """
    names = set()
    for klass in cls.__mro__:
        if klass is object:
            continue
        names |= _own_names(klass)
    return names


def splice_extension_bases(cls, extensions):
    """
    Return a class equivalent to `cls` but with the given plugin extension mixin classes spliced into its bases,
    so that fields/filters they declare are picked up when the class is processed by Strawberry.

    If `extensions` is empty, `cls` is returned unchanged (an exact pass-through). Otherwise a new class is built
    with the same name and namespace as `cls` — preserving its own annotations, fields, and methods — with the
    extension classes appended to its bases.

    Precedence: extensions are appended *after* `cls`'s base classes in the MRO, so extensions are strictly
    additive. Any name the core type already provides (its own fields or anything it inherits, including hooks such
    as `get_queryset`) always wins; an extension declaring such a name is ignored. When two extensions declare the
    same new name, the one whose plugin loaded first wins (it is registered earlier). Both cases are warned about.
    """
    if not extensions:
        return cls

    # Fetch the logger lazily rather than at module import. Importing this module during settings/app loading
    # (e.g. via the plugin registration helpers) happens before Django configures logging; creating the logger
    # then would get it disabled by a `disable_existing_loggers` LOGGING config.
    logger = logging.getLogger('netbox.graphql')

    # Warn on field-name collisions so they can be diagnosed in deployments with many plugins.
    core_names = _core_names(cls)
    seen = {}
    for extension in extensions:
        for name in _own_names(extension):
            if name in core_names:
                logger.warning(
                    "GraphQL extension %s declares '%s', which core type %s already provides; the extension's "
                    "version is ignored (core takes precedence).",
                    extension, name, cls.__name__,
                )
            elif name in seen:
                logger.warning(
                    "GraphQL extensions %s and %s both define '%s' on %s; %s takes precedence because its "
                    "plugin is loaded first.",
                    seen[name], extension, name, cls.__name__, seen[name],
                )
            else:
                seen[name] = extension

    namespace = dict(cls.__dict__)
    # Drop the descriptors that cannot (and need not) be copied to the rebuilt class; they are recreated by the
    # metaclass call below.
    namespace.pop('__dict__', None)
    namespace.pop('__weakref__', None)

    bases = (*cls.__bases__, *extensions)
    # Rebuild via the class's own metaclass rather than the built-in `type`, so a core type using a custom
    # metaclass is preserved. Pre-decoration Strawberry/dataclass types use the plain `type` metaclass.
    try:
        return type(cls)(cls.__name__, bases, namespace)
    except TypeError as exc:
        raise TypeError(
            f"Failed to splice GraphQL extension(s) {[e.__name__ for e in extensions]} into core type "
            f"'{cls.__name__}': {exc}. A GraphQL extension should be a plain @strawberry.type mixin that only "
            f"adds fields; inheriting from classes already in the core type's base list can produce an "
            f"inconsistent MRO."
        ) from exc


def register_model_graphql_type(model, delegate, store_key, **kwargs):
    """
    Shared implementation behind `register_type` and `register_filter`. Returns a decorator that splices any
    plugin extensions for `model` (from `store_key`) into the decorated class, then delegates to `delegate`
    (`strawberry_django.type` / `filter_type`).

    The registry is read at decoration (import) time. This is safe because the schema is assembled lazily from the
    URLconf, after every plugin's `ready()` has run; importing a core `graphql/types.py` during app init would read
    the registry too early and silently drop later-registered extensions.
    """
    label = get_model_label(model)

    def wrapper(cls):
        # Record that this type/filter has been assembled, so a plugin that registers an extension after this
        # point (e.g. because its ready() imported a core graphql module early) can be warned it is too late.
        registry['plugins']['graphql_extensions_assembled'].add((store_key, label))
        extensions = registry['plugins'][store_key].get(label)
        cls = splice_extension_bases(cls, extensions)
        return delegate(model, **kwargs)(cls)

    return wrapper
