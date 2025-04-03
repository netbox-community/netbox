from django.core.checks import Error, register, Tags
from django.db.models import Index, UniqueConstraint
from django.apps import apps

__all__ = (
    'check_duplicate_indexes',
)


@register(Tags.models)
def check_duplicate_indexes(app_configs, **kwargs):
    """
    Check for an index which is redundant to a declared unique constraint.
    """
    errors = []

    for model in apps.get_models():
        if not (meta := getattr(model, "_meta", None)):
            continue

        index_fields = {
            tuple(index.fields) for index in getattr(meta, 'indexes', [])
            if isinstance(index, Index)
        }
        constraint_fields = {
            tuple(constraint.fields) for constraint in getattr(meta, 'constraints', [])
            if isinstance(constraint, UniqueConstraint)
        }

        # Find overlapping definitions
        if duplicated := index_fields & constraint_fields:
            for fields in duplicated:
                errors.append(
                    Error(
                        f"Model '{model.__name__}' defines the same field set {fields} in both `Meta.indexes` and "
                        f"`Meta.constraints`.",
                        obj=model,
                    )
                )

    return errors
