import decimal

from django.core.serializers.json import DjangoJSONEncoder

__all__ = (
    'ConfigJSONEncoder',
    'CustomFieldJSONEncoder',
)


class CustomFieldJSONEncoder(DjangoJSONEncoder):
    """
    Override Django's built-in JSON encoder to save decimal values as JSON numbers.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


class ConfigJSONEncoder(DjangoJSONEncoder):
    """
    Override Django's built-in JSON encoder to serialize CustomValidator classes as strings.
    """
    def default(self, o):
        from extras.validators import CustomValidator

        if issubclass(type(o), CustomValidator):
            return type(o).__name__

        return super().default(o)
