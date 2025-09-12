import decimal
import json

from django.core.serializers.json import DjangoJSONEncoder

from utilities.datetime import datetime_from_timestamp

__all__ = (
    'ConfigJSONEncoder',
    'CustomFieldJSONEncoder',
    'JobLogDecoder',
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


class JobLogDecoder(json.JSONDecoder):
    """
    Deserialize JobLogEntry timestamps.
    """
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self._deserialize_entry
        super().__init__(*args, **kwargs)

    def _deserialize_entry(self, obj: dict) -> dict:
        if obj.get('timestamp'):
            # Deserialize a timestamp string to a native datetime object
            try:
                obj['timestamp'] = datetime_from_timestamp(obj['timestamp'])
            except ValueError:
                pass
        return obj
