from django.db.models import ManyToOneRel
from django.utils import timezone
from django.utils.timezone import localtime

from .string import title


def dynamic_import(name):
    """
    Dynamically import a class from an absolute path string
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def content_type_name(ct, include_app=True):
    """
    Return a human-friendly ContentType name (e.g. "DCIM > Site").
    """
    try:
        meta = ct.model_class()._meta
        app_label = title(meta.app_config.verbose_name)
        model_name = title(meta.verbose_name)
        if include_app:
            return f'{app_label} > {model_name}'
        return model_name
    except AttributeError:
        # Model no longer exists
        return f'{ct.app_label} > {ct.model}'


def content_type_identifier(ct):
    """
    Return a "raw" ContentType identifier string suitable for bulk import/export (e.g. "dcim.site").
    """
    return f'{ct.app_label}.{ct.model}'


def local_now():
    """
    Return the current date & time in the system timezone.
    """
    return localtime(timezone.now())


def get_related_models(model, ordered=True):
    """
    Return a list of all models which have a ForeignKey to the given model and the name of the field. For example,
    `get_related_models(Tenant)` will return all models which have a ForeignKey relationship to Tenant.
    """
    related_models = [
        (field.related_model, field.remote_field.name)
        for field in model._meta.related_objects
        if type(field) is ManyToOneRel
    ]

    if ordered:
        return sorted(related_models, key=lambda x: x[0]._meta.verbose_name.lower())

    return related_models
