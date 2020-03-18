class Registry(dict):
    """
    Central registry for registration of functionality. Once a store (key) is defined, it cannot be overwritten or
    deleted (although its value may be manipulated).
    """
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise Exception("Invalid store: {}".format(key))

    def __setitem__(self, key, value):
        if key in self:
            raise Exception("Store already set: {}".format(key))
        super().__setitem__(key, value)

    def __delitem__(self, key):
        raise Exception("Cannot delete stores from registry")


registry = Registry()
