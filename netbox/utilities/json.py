import decimal

from django.core.serializers.json import DjangoJSONEncoder

__all__ = (
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
