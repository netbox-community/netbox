from django.db.models import ManyToOneRel


def dynamic_import(name):
    """
    Dynamically import a class from an absolute path string
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


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
