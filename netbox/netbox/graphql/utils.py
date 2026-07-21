import logging

__all__ = (
    'splice_extension_bases',
)

logger = logging.getLogger('netbox.graphql')


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
    Return the set of names already provided by `cls` and its base classes (i.e. everything resolvable on the core
    type before any extension is spliced in). Used to detect extensions that shadow core fields or hooks.
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
    extension classes prepended to its bases.

    Precedence: extensions are prepended *ahead* of `cls`'s base classes in the MRO. A name defined directly in
    `cls`'s own body still wins, but a name only *inherited* by `cls` (e.g. `get_queryset` from BaseObjectType, or
    a field from an organizational base) is overridden by an extension that declares the same name. This lets a
    misbehaving extension shadow core behavior — including permission-enforcing hooks — so collisions are logged
    below, but they are not prevented (plugin code is trusted).
    """
    if not extensions:
        return cls

    # Warn on field-name collisions. Two classes of collision are surfaced: (1) an extension shadowing a name the
    # core type already provides (more dangerous — may override a permission hook or core field), and (2) two
    # extensions redefining the same name (the winner is resolved by MRO and depends on plugin load order). Both
    # are hard to diagnose in deployments with many plugins.
    core_names = _core_names(cls)
    seen = {}
    for extension in extensions:
        for name in _own_names(extension):
            if name in core_names:
                logger.warning(
                    "GraphQL extension %s redefines '%s', which is already provided by core type %s; "
                    "the extension overrides the core field/hook via MRO.",
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

    namespace = dict(cls.__dict__)
    # Drop the descriptors that cannot (and need not) be copied to the rebuilt class; they are recreated by the
    # metaclass call below.
    namespace.pop('__dict__', None)
    namespace.pop('__weakref__', None)

    bases = (*extensions, *cls.__bases__)
    # Rebuild via the class's own metaclass rather than the built-in `type`, so a core type using a custom
    # metaclass is preserved. Pre-decoration Strawberry/dataclass types use the plain `type` metaclass.
    return type(cls)(cls.__name__, bases, namespace)
