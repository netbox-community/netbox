from .register import register_search


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
