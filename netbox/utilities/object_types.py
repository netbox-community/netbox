from .string import title

__all__ = (
    'object_type_identifier',
    'object_type_name',
)


def object_type_identifier(object_type):
    """
    Return a "raw" ObjectType identifier string suitable for bulk import/export (e.g. "dcim.site").
    """
    return f'{object_type.app_label}.{object_type.model}'


def object_type_name(object_type, include_app=True):
    """
    Return a human-friendly ObjectType name (e.g. "DCIM > Site").
    """
    try:
        meta = object_type.model_class()._meta
        app_label = title(meta.app_config.verbose_name)
        model_name = title(meta.verbose_name)
        if include_app:
            return f'{app_label} > {model_name}'
        return model_name
    except AttributeError:
        # Model does not exist
        return f'{object_type.app_label} > {object_type.model}'
