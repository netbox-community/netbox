from django.core.exceptions import ImproperlyConfigured

from netbox.registry import registry

__all__ = (
    'get_model_label',
    'register_model_graphql_type',
)


def get_model_label(model):
    """
    Return the canonical `app_label.model_name` label used to key GraphQL extensions in the registry. Both the
    registration side and the lookup side must derive labels through this helper so they always agree.
    """
    return f'{model._meta.app_label}.{model._meta.model_name}'


def _own_names(klass):
    """Concrete attributes only, since PEP 649 keeps annotations out of the class dict from Python 3.14 on."""
    names = {name for name in vars(klass) if not name.startswith('__')}
    names.discard('models')
    return names


def _field_names(klass):
    """Python names from the class's own completed Strawberry definition, including fields it inherited."""
    definition = vars(klass).get('__strawberry_definition__')
    if definition is None:
        return set()
    return {field.python_name for field in definition.fields if field.python_name is not None} - {'models'}


def _all_names(klass):
    """Strawberry fields plus concrete attributes anywhere in the MRO, so no raw annotation is ever read."""
    names = _field_names(klass)
    for base in klass.__mro__:
        if base is not object:
            names |= _own_names(base)
    return names


def _name_owner(klass, name):
    """Class in the MRO declaring `name` as a real attribute, or None when it is annotation-only."""
    for base in klass.__mro__:
        if name in vars(base):
            return base
    return None


def _core_names(cls):
    """
    Return every name `cls` resolves (its own body and everything it inherits). Extensions are spliced in *after*
    these bases, so any name already present here is provided by the core type and an extension cannot override it.
    """
    names = _field_names(cls)
    for klass in cls.__mro__:
        if klass is object:
            continue
        names |= _own_names(klass)
    return names


def _class_path(cls):
    """Module-qualified identity for startup errors, since bare class names collide across plugins."""
    return f'{cls.__module__}.{cls.__qualname__}'


def _compose(cls, extensions):
    """
    Build a subclass of `cls` with the extension mixins appended to its bases. `cls` is already decorated, so
    the composed class needs no namespace of its own: fields and methods are inherited, zero-argument super()
    in core methods keeps working, and core attributes win every MRO lookup.
    """
    namespace = {'__module__': cls.__module__, '__qualname__': cls.__qualname__, '__doc__': cls.__doc__}
    try:
        return type(cls)(cls.__name__, (cls, *extensions), namespace)
    except TypeError as exc:
        raise ImproperlyConfigured(
            f"Failed to compose GraphQL extension(s) {[_class_path(e) for e in extensions]} into core type "
            f"'{cls.__name__}': {exc}. A GraphQL extension should be a plain @strawberry.type mixin that only "
            f"adds fields. The extensions declare conflicting base class orders."
        ) from exc


def splice_extension_bases(cls, extensions):
    """
    Return `cls` composed with the given extension mixins, or `cls` unchanged when there are none. Extensions are
    strictly additive. An extension sharing ancestry with the core type, declaring a Python name the core type
    already resolves, or declaring a name another extension claims raises ImproperlyConfigured.
    """
    if not extensions:
        return cls
    core_names = _core_names(cls)
    core_bases = set(cls.__mro__)
    claimed = {}
    for extension in extensions:
        # A shared ancestor lets C3 interleave extension bases ahead of core hooks such as get_queryset().
        if shared := [base for base in extension.__mro__ if base is not object and base in core_bases]:
            raise ImproperlyConfigured(
                f"GraphQL extension {_class_path(extension)} shares ancestry with core type "
                f"'{cls.__name__}' ({_class_path(shared[0])}). An extension must be an independent "
                f"mixin that does not inherit from core GraphQL classes."
            )
        for name in _all_names(extension):
            if name in core_names:
                raise ImproperlyConfigured(
                    f"GraphQL extension {_class_path(extension)} declares '{name}', which core type "
                    f"'{cls.__name__}' already provides."
                )
            if name in claimed:
                # One shared helper base is harmless, two independent declarations of a name are not.
                owner = _name_owner(extension, name)
                if owner is None or owner is not _name_owner(claimed[name], name):
                    raise ImproperlyConfigured(
                        f"GraphQL extensions {_class_path(claimed[name])} and {_class_path(extension)} both "
                        f"declare '{name}' on '{cls.__name__}'."
                    )
            claimed[name] = extension
    return _compose(cls, extensions)


def validate_extension_final_names(core_type, extensions):
    """
    Check extension fields against the final GraphQL names and python names of the decorated, unextended core
    type. This covers names invisible before decoration: generated model fields, filter logical fields (AND,
    OR, NOT, DISTINCT), and explicit aliases. NetBox disables auto camel casing, so a field's final name is
    its explicit graphql_name or its python name.
    """
    baseline_fields = core_type.__strawberry_definition__.fields
    baseline_names = {f.graphql_name or f.python_name for f in baseline_fields}
    baseline_python_names = {f.python_name for f in baseline_fields}
    claimed_names = {}
    claimed_python_names = {}
    for extension in extensions:
        for field in extension.__strawberry_definition__.fields:
            name = field.graphql_name or field.python_name
            if name in baseline_names:
                raise ImproperlyConfigured(
                    f"GraphQL extension {_class_path(extension)} declares field '{name}', which collides with an "
                    f"existing field of that name on '{core_type.__name__}'."
                )
            # An aliased field still claims its python name and would suppress the generated core field.
            if field.python_name in baseline_python_names:
                raise ImproperlyConfigured(
                    f"GraphQL extension {_class_path(extension)} declares '{field.python_name}', which core type "
                    f"'{core_type.__name__}' already provides."
                )
            # Strawberry keys fields by python name, so a shared one silently replaces across extensions.
            if field.python_name in claimed_python_names:
                raise ImproperlyConfigured(
                    f"GraphQL extensions {_class_path(claimed_python_names[field.python_name])} and "
                    f"{_class_path(extension)} both declare '{field.python_name}' on '{core_type.__name__}'."
                )
            if name in claimed_names:
                raise ImproperlyConfigured(
                    f"GraphQL extensions {_class_path(claimed_names[name])} and {_class_path(extension)} both "
                    f"declare field '{name}' on '{core_type.__name__}'."
                )
            claimed_python_names[field.python_name] = extension
            claimed_names[name] = extension


def validate_extension_targets():
    """
    Reject extensions whose target model never assembled a GraphQL type or filter, since they would otherwise
    be silently discarded. Runs from the finalizer app after schema assembly.
    """
    assembled = registry['plugins']['graphql_extensions_assembled']
    for store in ('graphql_type_extensions', 'graphql_filter_extensions'):
        for label, extensions in registry['plugins'][store].items():
            if extensions and (store, label) not in assembled:
                classes = ', '.join(_class_path(extension) for extension in extensions)
                kind = 'output type' if store == 'graphql_type_extensions' else 'filter'
                raise ImproperlyConfigured(
                    f"GraphQL extension target '{label}' has no registered {kind} for extension(s): {classes}."
                )


def register_model_graphql_type(model, delegate, store_key, **kwargs):
    """
    Decorator factory composing registered plugin extensions into a core GraphQL type or filter class. The
    finalizer app assembles the schema during django.setup(), after every plugin has initialized, and
    registering an extension once its target has assembled raises through the assembled-target set.
    """
    label = get_model_label(model)

    def wrapper(cls):
        own_is_type_of = vars(cls).get('is_type_of')
        core_type = delegate(model, **kwargs)(cls)
        registry['plugins']['graphql_extensions_assembled'].add((store_key, label))
        extensions = registry['plugins'][store_key].get(label)
        if not extensions:
            return core_type
        validate_extension_final_names(core_type, extensions)
        composed = splice_extension_bases(core_type, extensions)
        # Only an is_type_of in the core's own body needs this, strawberry_django chains inherited ones itself.
        if own_is_type_of is not None:
            composed.is_type_of = own_is_type_of
        return delegate(model, **kwargs)(composed)

    return wrapper
