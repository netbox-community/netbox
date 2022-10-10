from extras.registry import registry


class SearchIndex:
    """
    Base class for building search indexes.
    """
    search_index = True

    @classmethod
    def get_category(cls):
        if hasattr(cls, 'category'):
            return cls.category
        return cls.model._meta.app_config.verbose_name


def register_search():
    def _wrapper(cls):
        model = cls.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        registry['search'][app_label][model_name] = cls

        return cls

    return _wrapper
