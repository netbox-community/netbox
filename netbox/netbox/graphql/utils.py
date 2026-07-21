import inspect
import logging

from netbox.registry import registry

__all__ = (
    'get_model_label',
    'register_model_graphql_type',
    'splice_extension_bases',
)

# Attributes an extension is not permitted to override. `get_queryset` enforces object-level permissions on the
# core type's queryset; letting a plugin shadow it via the spliced MRO would silently bypass that enforcement.
PROTECTED_ATTRS = frozenset({
    'get_queryset',
    'get_object',
})


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


def _inherited_names(cls):
    """
    Return the set of names `cls` resolves only through its base classes (i.e. not defined in its own body). A
    spliced extension is prepended ahead of these bases, so an extension declaring one of these names overrides it
    via the MRO. Names in `cls`'s own body are excluded here because the rebuilt class carries them in its own
    namespace, where they take precedence over any extension.
    """
    names = set()
    for klass in cls.__mro__:
        if klass in (cls, object):
            continue
        names |= _own_names(klass)
    return names - _own_names(cls)


def splice_extension_bases(cls, extensions):
    """
    Return a class equivalent to `cls` but with the given plugin extension mixin classes spliced into its bases,
    so that fields/filters they declare are picked up when the class is processed by Strawberry.

    If `extensions` is empty, `cls` is returned unchanged (an exact pass-through). Otherwise a new class is built
    with the same name and namespace as `cls` — preserving its own annotations, fields, and methods — with the
    extension classes prepended to its bases.

    Precedence: extensions are prepended *ahead* of `cls`'s base classes in the MRO. A name defined directly in
    `cls`'s own body still wins over an extension; a name `cls` only *inherits* is overridden by an extension that
    declares it. As an exception, the attributes in `PROTECTED_ATTRS` (notably `get_queryset`) are pinned into the
    rebuilt class's own namespace so a plugin can never shadow the core permission-enforcing hooks; an extension
    that tries to redefine one is ignored (and warned about).
    """
    if not extensions:
        return cls

    # Fetch the logger lazily rather than at module import. Importing this module during settings/app loading
    # (e.g. via the plugin registration helpers) happens before Django configures logging; creating the logger
    # then would get it disabled by a `disable_existing_loggers` LOGGING config.
    logger = logging.getLogger('netbox.graphql')

    namespace = dict(cls.__dict__)
    # Drop the descriptors that cannot (and need not) be copied to the rebuilt class; they are recreated by the
    # metaclass call below.
    namespace.pop('__dict__', None)
    namespace.pop('__weakref__', None)

    # Pin the protected hooks into the rebuilt class's own body (unless `cls` already defines them directly) so
    # that a prepended extension cannot override them via the MRO.
    pinned = set()
    for name in PROTECTED_ATTRS:
        if name in namespace:
            continue
        attr = inspect.getattr_static(cls, name, None)
        if attr is not None:
            namespace[name] = attr
            pinned.add(name)

    # Names `cls` defines in its own body (which win over any extension) vs. names it only inherits (which an
    # extension overrides via the MRO). Pinned hooks are treated as own-body names.
    core_own = _own_names(cls) | pinned
    core_inherited = _inherited_names(cls) - pinned

    # Warn on field-name collisions so they can be diagnosed in deployments with many plugins.
    seen = {}
    for extension in extensions:
        for name in _own_names(extension):
            if name in pinned:
                logger.warning(
                    "GraphQL extension %s attempts to redefine the protected hook '%s' on core type %s; "
                    "the core implementation is preserved and the extension's version is ignored.",
                    extension, name, cls.__name__,
                )
            elif name in core_own:
                logger.warning(
                    "GraphQL extension %s declares '%s', which core type %s defines directly; the core "
                    "definition takes precedence and the extension's version is ignored.",
                    extension, name, cls.__name__,
                )
            elif name in core_inherited:
                logger.warning(
                    "GraphQL extension %s overrides '%s', which core type %s inherits; the extension's "
                    "version takes precedence via MRO.",
                    extension, name, cls.__name__,
                )
            if name in seen:
                logger.warning(
                    "GraphQL extension %s redefines field '%s' on %s, already introduced by %s; "
                    "the effective field is resolved by MRO and depends on plugin load order.",
                    extension, name, cls.__name__, seen[name],
                )
            else:
                seen[name] = extension

    bases = (*extensions, *cls.__bases__)
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
        extensions = registry['plugins'][store_key].get(label)
        cls = splice_extension_bases(cls, extensions)
        return delegate(model, **kwargs)(cls)

    return wrapper
