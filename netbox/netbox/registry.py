import collections


class Registry(dict):
    """
    Central registry for registration of functionality. Once a Registry is initialized, keys cannot be added or
    removed (though the value of each key is mutable).
    """
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise KeyError(f"Invalid store: {key}")

    def __setitem__(self, key, value):
        raise TypeError("Cannot add stores to registry after initialization")

    def __delitem__(self, key):
        raise TypeError("Cannot delete stores from registry")


# Initialize the global registry
registry = Registry({
    'counter_fields': collections.defaultdict(dict),
    'data_backends': dict(),
    'denormalized_fields': collections.defaultdict(list),
    'model_features': dict(),
    'models': collections.defaultdict(set),
    'plugins': dict(),
    'search': dict(),
    'tables': collections.defaultdict(dict),
    'views': collections.defaultdict(dict),
    'widgets': dict(),
})
