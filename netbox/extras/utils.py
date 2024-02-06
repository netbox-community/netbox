from taggit.managers import _TaggableManager

from netbox.registry import registry


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

    return '{}{}_{}_{}'.format(path, instance.content_type.name, instance.object_id, filename)


def register_features(model, features):
    """
    Register model features in the application registry.
    """
    app_label, model_name = model._meta.label_lower.split('.')
    for feature in features:
        try:
            registry['model_features'][feature][app_label].add(model_name)
        except KeyError:
            raise KeyError(
                f"{feature} is not a valid model feature! Valid keys are: {registry['model_features'].keys()}"
            )

    # Register public models
    if not getattr(model, '_netbox_private', False):
        registry['models'][app_label].add(model_name)


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
