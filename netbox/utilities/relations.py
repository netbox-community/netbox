from django.db.models import ManyToOneRel

__all__ = (
    'get_related_models',
)


def get_related_models(model, ordered=True, include_hidden=False):
    """
    Return a list of all models which have a ForeignKey to the given model and the name of the field. For example,
    `get_related_models(Tenant)` will return all models which have a ForeignKey relationship to Tenant. Set
    `include_hidden` to also return relationships declared with `related_name='+'`, excluding the
    automatically created models behind many-to-many fields.
    """
    related_models = [
        (field.related_model, field.remote_field.name)
        for field in model._meta.get_fields(include_hidden=include_hidden)
        if type(field) is ManyToOneRel
        and not field.related_model._meta.auto_created
        and not getattr(field.related_model, '_netbox_private', False)
    ]

    if ordered:
        return sorted(related_models, key=lambda x: x[0]._meta.verbose_name.lower())

    return related_models
