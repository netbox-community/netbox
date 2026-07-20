__all__ = (
    'splice_extension_bases',
)


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

    namespace = dict(cls.__dict__)
    # Drop the descriptors that cannot (and need not) be copied to the rebuilt class; they are recreated by type().
    namespace.pop('__dict__', None)
    namespace.pop('__weakref__', None)

    bases = (*extensions, *cls.__bases__)
    return type(cls.__name__, bases, namespace)
