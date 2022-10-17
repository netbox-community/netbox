from collections import namedtuple

from django.db import models

from extras.registry import registry

ObjectFieldValue = namedtuple('ObjectFieldValue', ('name', 'type', 'weight', 'value'))


class FieldTypes:
    FLOAT = 'float'
    INTEGER = 'int'
    STRING = 'str'


class LookupTypes:
    PARTIAL = 'icontains'
    EXACT = 'iexact'
    STARTSWITH = 'istartswith'
    ENDSWITH = 'iendswith'


def get_registry():
    r = {}
    for app_label, models in registry['search'].items():
        for model_name, idx in models.items():
            r[f'{app_label}.{model_name}'] = idx

    return r


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

    @staticmethod
    def get_field_type(instance, field_name):
        field_cls = instance._meta.get_field(field_name).__class__
        if issubclass(field_cls, (models.FloatField, models.DecimalField)):
            return FieldTypes.FLOAT
        if issubclass(field_cls, models.IntegerField):
            return FieldTypes.INTEGER
        return FieldTypes.STRING

    @staticmethod
    def get_field_value(instance, field_name):
        return str(getattr(instance, field_name))

    @classmethod
    def to_cache(cls, instance):
        values = []

        # Capture built-in fields
        for name, weight in cls.fields:
            type_ = cls.get_field_type(instance, name)
            value = cls.get_field_value(instance, name)
            values.append(
                ObjectFieldValue(name, type_, weight, value)
            )

        # Capture custom fields
        if hasattr(instance, 'custom_field_data'):
            for cf, value in instance.get_custom_fields().items():
                type_ = cf.search_type
                value = instance.custom_field_data.get(cf.name)
                weight = cf.search_weight
                if not type_ or not value or not weight:
                    continue
                values.append(
                    ObjectFieldValue(f'cf_{cf.name}', type_, weight, value)
                )

        return values


class SearchResult:
    """
    Represents a single result returned by a search backend's search() method.
    """
    def __init__(self, obj, field=None, value=None):
        self.object = obj
        self.field = field
        self.value = value


def register_search():
    """
    Decorator for registering a SearchIndex with a particular model.
    """
    def _wrapper(cls):
        model = cls.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        registry['search'][app_label][model_name] = cls

        return cls

    return _wrapper
