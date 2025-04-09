import importlib

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import Q
from taggit.managers import _TaggableManager

from netbox.context import current_request
from .validators import CustomValidator

__all__ = (
    'SharedObjectViewMixin',
    'image_upload',
    'is_report',
    'is_script',
    'is_taggable',
    'run_validators',
)


class SharedObjectViewMixin:

    def get_queryset(self, request):
        """
        Return only shared objects, or those owned by the current user, unless this is a superuser.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if request.user.is_anonymous:
            return queryset.filter(shared=True)
        return queryset.filter(
            Q(shared=True) | Q(user=request.user)
        )


def filename_from_model(model: models.Model) -> str:
    """Standardises how we generate filenames from model class for exports"""
    base = model._meta.verbose_name_plural.lower().replace(' ', '_')
    return f'netbox_{base}'


def filename_from_object(context: dict) -> str:
    """Standardises how we generate filenames from model class for exports"""
    if 'device' in context:
        base = f"{context['device'].name or 'config'}"
    elif 'virtualmachine' in context:
        base = f"{context['virtualmachine'].name or 'config'}"
    else:
        base = 'config'
    return base


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
    if instance.name and extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp']:
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
