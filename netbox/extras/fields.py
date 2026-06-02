from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField, TextField

__all__ = (
    'CachedValueField',
    'ChoiceSetField',
)


class CachedValueField(TextField):
    """
    Currently a dummy field to prevent custom lookups being applied globally to TextField.
    """
    pass


class ChoiceSetField(ArrayField):
    """
    An ArrayField of two-element [value, label] string pairs representing custom field choices.
    """
    def __init__(self, **kwargs):
        kwargs['base_field'] = ArrayField(base_field=CharField(max_length=100), size=2)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # base_field is fixed by __init__ and omitted from migrations
        del kwargs['base_field']
        return name, path, args, kwargs
