"""
Extracted, composable validators for tenancy models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# ContactAssignment
# ──────────────────────────────────────────────────────────────────────

def validate_contactassignment_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.object_type, 'contacts'):
        raise ValidationError(
            _("Contacts cannot be assigned to this object type ({type}).").format(type=instance.object_type)
        )


validator_registry.register('tenancy.contactassignment',
    ModelValidator(
        name='contactassignment_feature',
        model_label='tenancy.contactassignment',
        fields=_fs({'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_contactassignment_feature,
        description='Object type must support contacts feature',
    ),
)
