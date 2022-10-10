from extras.registry import registry


class SearchIndex:
    """
    Base class for building search indexes.

    Attrs:
        model: The model class for which this index is used.
    """
    model = None
    fields = ()

    @classmethod
    def get_category(cls):
        """
        Return the title of the search category under which this model is registered.
        """
        if hasattr(cls, 'category'):
            return cls.category
        return cls.model._meta.app_config.verbose_name

    @classmethod
    def to_cache(cls, instance):
        return [
            (field, str(getattr(instance, field)), weight)
            for field, weight in cls.fields
        ]


def register_search():
    def _wrapper(cls):
        model = cls.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        registry['search'][app_label][model_name] = cls

        return cls

    return _wrapper
