from django.db.models import UniqueConstraint
from rest_framework.utils.field_mapping import get_unique_error_message
from rest_framework.validators import UniqueValidator

__all__ = (
    'get_unique_validators',
)


def get_unique_validators(field_name, model_field):
    """
    Extend Django REST Framework's get_unique_validators() function to attach a UniqueValidator to a field *only* if the
     associated UniqueConstraint does NOT have a condition which references another field. See bug #19302.
    """
    field_set = {field_name}
    conditions = {
        c.condition
        for c in model_field.model._meta.constraints
        if isinstance(c, UniqueConstraint) and set(c.fields) == field_set
    }

    # START custom logic
    conditions = {
        cond for cond in conditions
        if cond is None or cond.referenced_base_fields == field_set
    }
    # END custom logic

    if getattr(model_field, 'unique', False):
        conditions.add(None)
    if not conditions:
        return
    unique_error_message = get_unique_error_message(model_field)
    queryset = model_field.model._default_manager
    for condition in conditions:
        yield UniqueValidator(
            queryset=queryset if condition is None else queryset.filter(condition),
            message=unique_error_message
        )
