import importlib

from django.core.exceptions import ImproperlyConfigured
from taggit.managers import _TaggableManager

from netbox.context import current_request
from .validators import CustomValidator

__all__ = (
    'image_upload',
    'is_report',
    'is_script',
    'is_taggable',
    'run_validators',
)


def is_taggable(obj):
    """
    Return True if the instance can have Tags assigned to it; False otherwise.
    """
    if hasattr(obj, 'tags'):
        if issubclass(obj.tags.__class__, _TaggableManager):
            return True
    return False


def image_upload(instance, filename):
    """
    Return a path for uploading image attachments.
    """
    path = 'image-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name and extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png']:
        filename = '.'.join([instance.name, extension])
    elif instance.name:
        filename = instance.name

    return '{}{}_{}_{}'.format(path, instance.object_type.name, instance.object_id, filename)


def is_script(obj):
    """
    Returns True if the object is a Script or Report.
    """
    from .reports import Report
    from .scripts import Script
    try:
        return (issubclass(obj, Report) and obj != Report) or (issubclass(obj, Script) and obj != Script)
    except TypeError:
        return False


def is_report(obj):
    """
    Returns True if the given object is a Report.
    """
    from .reports import Report
    try:
        return issubclass(obj, Report) and obj != Report
    except TypeError:
        return False


def run_validators(instance, validators):
    """
    Run the provided iterable of CustomValidators for the instance.
    """
    request = current_request.get()
    for validator in validators:

        # Loading a validator class by dotted path
        if type(validator) is str:
            module, cls = validator.rsplit('.', 1)
            validator = getattr(importlib.import_module(module), cls)()

        # Constructing a new instance on the fly from a ruleset
        elif type(validator) is dict:
            validator = CustomValidator(validator)

        elif not issubclass(validator.__class__, CustomValidator):
            raise ImproperlyConfigured(f"Invalid value for custom validator: {validator}")

        validator(instance, request)
