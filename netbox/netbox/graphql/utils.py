import logging

__all__ = (
    'splice_extension_bases',
)

logger = logging.getLogger('netbox.graphql')


def _extension_field_names(extension):
    """
    Return the set of field/filter names an extension class contributes directly (annotations and its own
    non-dunder attributes such as resolver methods), excluding the `models` marker.
    """
    names = set(getattr(extension, '__annotations__', {}))
    names |= {name for name in vars(extension) if not name.startswith('__')}
    names.discard('models')
    return names


def splice_extension_bases(cls, extensions):
    """
    Return a class equivalent to `cls` but with the given plugin extension mixin classes spliced into its bases,
    so that fields/filters they declare are picked up when the class is processed by Strawberry.

    If `extensions` is empty, `cls` is returned unchanged (an exact pass-through). Otherwise a new class is built
    with the same name and namespace as `cls` — preserving its own annotations, fields, and methods — with the
    extension classes prepended to its bases.
    """
    if not extensions:
        return cls

    # Warn on field-name collisions between extensions targeting the same type. The MRO silently picks a
    # load-order-dependent winner, which is hard to diagnose in deployments with many plugins.
    seen = {}
    for extension in extensions:
        for name in _extension_field_names(extension):
            if name in seen:
                logger.warning(
                    "GraphQL extension %s redefines field '%s' on %s, already introduced by %s; "
                    "the effective field is resolved by MRO and depends on plugin load order.",
                    extension, name, cls.__name__, seen[name],
                )
            else:
                seen[name] = extension

    namespace = dict(cls.__dict__)
    # Drop the descriptors that cannot (and need not) be copied to the rebuilt class; they are recreated by type().
    namespace.pop('__dict__', None)
    namespace.pop('__weakref__', None)

    bases = (*extensions, *cls.__bases__)
    return type(cls.__name__, bases, namespace)
