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


class SearchIndex:
    """
    Base class for building search indexes.

    Attrs:
        model: The model class for which this index is used.
        category: The label of the group under which this indexer is categorized (for form field display). If none,
            the name of the model's app will be used.
        fields: An iterable of two-tuples defining the model fields to be indexed and the weight associated with each.
    """
    model = None
    category = None
    fields = ()

    @staticmethod
    def get_field_type(instance, field_name):
        """
        Return the data type of the specified model field.
        """
        field_cls = instance._meta.get_field(field_name).__class__
        if issubclass(field_cls, (models.FloatField, models.DecimalField)):
            return FieldTypes.FLOAT
        if issubclass(field_cls, models.IntegerField):
            return FieldTypes.INTEGER
        return FieldTypes.STRING

    @staticmethod
    def get_field_value(instance, field_name):
        """
        Return the value of the specified model field as a string.
        """
        return str(getattr(instance, field_name))

    @classmethod
    def get_category(cls):
        return cls.category or cls.model._meta.app_config.verbose_name

    @classmethod
    def to_cache(cls, instance, custom_fields=None):
        """
        Return a list of ObjectFieldValue representing the instance fields to be cached.

        Args:
            instance: The instance being cached.
            custom_fields: An iterable of CustomFields to include when caching the instance. If None, all custom fields
                defined for the model will be included. (This can also be provided during bulk caching to avoid looking
                up the available custom fields for each instance.)
        """
        values = []

        # Capture built-in fields
        for name, weight in cls.fields:
            type_ = cls.get_field_type(instance, name)
            value = cls.get_field_value(instance, name)
            if type_ and value:
                values.append(
                    ObjectFieldValue(name, type_, weight, value)
                )

        # Capture custom fields
        if getattr(instance, 'custom_field_data', None):
            if custom_fields is None:
                custom_fields = instance.get_custom_fields().keys()
            for cf in custom_fields:
                type_ = cf.search_type
                value = instance.custom_field_data.get(cf.name)
                weight = cf.search_weight
                if type_ and value and weight:
                    values.append(
                        ObjectFieldValue(f'cf_{cf.name}', type_, weight, value)
                    )

        return values


def get_indexer(model):
    """
    Get the search indexer class for the given model.
    """
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    return registry['search'][app_label][model_name]


def register_search(cls):
    """
    Decorator for registering a SearchIndex with a particular model.
    """
    model = cls.model
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    registry['search'][app_label][model_name] = cls

    return cls
