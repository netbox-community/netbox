import collections

from django.utils.translation import gettext as _


class Registry(dict):
    """
    Central registry for registration of functionality. Once a Registry is initialized, keys cannot be added or
    removed (though the value of each key is mutable).
    """
    def __getitem__(self, key):
        # TODO: Remove in NetBox v4.7
        if key == 'models':
            import warnings
            warnings.warn(
                'The "models" registry key is deprecated and will be removed in NetBox v4.7. Registered models can be '
                'obtained by calling ObjectType.objects.public().',
                DeprecationWarning,
                stacklevel=2,
            )
        try:
            return super().__getitem__(key)
        except KeyError:
            raise KeyError(_("Invalid store: {key}").format(key=key))

    def __setitem__(self, key, value):
        raise TypeError(_("Cannot add stores to registry after initialization"))

    def __delitem__(self, key):
        raise TypeError(_("Cannot delete stores from registry"))


# Initialize the global registry
registry = Registry({
    'counter_fields': collections.defaultdict(dict),
    'data_backends': dict(),
    'denormalized_fields': collections.defaultdict(list),
    'event_types': dict(),
    'filtersets': dict(),
    'model_actions': collections.defaultdict(set),
    'model_features': dict(),
    # TODO: Remove in NetBox v4.7
    'models': collections.defaultdict(set),
    'plugins': dict(),
    'request_processors': list(),
    'search': dict(),
    'system_jobs': dict(),
    'tables': collections.defaultdict(dict),
    'views': collections.defaultdict(dict),
    'webhook_callbacks': list(),
    'widgets': dict(),
})
