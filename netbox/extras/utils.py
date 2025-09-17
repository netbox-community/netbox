import importlib
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured, SuspiciousFileOperation
from django.core.files.storage import default_storage
from django.core.files.utils import validate_file_name
from django.db import models
from django.db.models import Q
from taggit.managers import _TaggableManager

from netbox.context import current_request

from .validators import CustomValidator

__all__ = (
    'SharedObjectViewMixin',
    'filename_from_model',
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
    """Standardizes how we generate filenames from model class for exports"""
    base = model._meta.verbose_name_plural.lower().replace(' ', '_')
    return f'netbox_{base}'


def filename_from_object(context: dict) -> str:
    """Standardizes how we generate filenames from model class for exports"""
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

    - Normalizes browser paths (e.g., C:\\fake_path\\photo.jpg)
    - Uses the instance.name if provided (sanitized to a *basename*, no ext)
    - Prefixes with a machine-friendly identifier

    Note: Relies on Django's default_storage utility.
    """
    upload_dir = 'image-attachments'
    default_filename = 'unnamed'
    allowed_img_extensions = ('bmp', 'gif', 'jpeg', 'jpg', 'png', 'webp')

    # Normalize Windows paths and create a Path object.
    normalized_filename = str(filename).replace('\\', '/')
    file_path = Path(normalized_filename)

    # Extract the extension from the uploaded file.
    ext = file_path.suffix.lower().lstrip('.')

    # Use the instance-provided name if available; otherwise use the file stem.
    # Rely on Django's get_valid_filename to perform sanitization.
    stem = (instance.name or file_path.stem).strip()
    try:
        safe_stem = default_storage.get_valid_name(stem)
    except SuspiciousFileOperation:
        safe_stem = default_filename

    # Append the uploaded extension only if it's an allowed image type
    final_name = f"{safe_stem}.{ext}" if ext in allowed_img_extensions else safe_stem

    # Create a machine-friendly prefix from the instance
    prefix = f"{instance.object_type.model}_{instance.object_id}"
    name_with_path = f"{upload_dir}/{prefix}_{final_name}"

    # Validate the generated relative path (blocks absolute/traversal)
    validate_file_name(name_with_path, allow_relative_path=True)
    return name_with_path


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

        # Loading a validator class by a dotted path
        if type(validator) is str:
            module, cls = validator.rsplit('.', 1)
            validator = getattr(importlib.import_module(module), cls)()

        # Constructing a new instance on the fly from a ruleset
        elif type(validator) is dict:
            validator = CustomValidator(validator)

        elif not issubclass(validator.__class__, CustomValidator):
            raise ImproperlyConfigured(f"Invalid value for custom validator: {validator}")

        validator(instance, request)
