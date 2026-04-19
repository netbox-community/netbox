"""
Extracted, composable validators for mixin models (WeightMixin, DistanceMixin,
NestedGroupModel, CustomFieldsMixin).

Per-model validators are registered directly against concrete model labels.
Mixin-level validators use the sentinel pattern (see CustomFieldsMixin section).
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# WeightMixin
# ──────────────────────────────────────────────────────────────────────

def validate_weight_unit_required(instance):
    if instance.weight and not instance.weight_unit:
        raise ValidationError(_("Must specify a unit when setting a weight"))


_weight_mixin_models = [
    'dcim.devicetype',
    'dcim.moduletype',
    'dcim.racktype',
    'dcim.rack',
]

for _label in _weight_mixin_models:
    validator_registry.register(_label,
        ModelValidator(
            name='weight_unit_required',
            model_label=_label,
            fields=_fs({'weight', 'weight_unit'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_weight_unit_required,
            description='Weight requires a unit',
        ),
    )

# ──────────────────────────────────────────────────────────────────────
# DistanceMixin
# ──────────────────────────────────────────────────────────────────────

def validate_distance_unit_required(instance):
    if instance.distance and not instance.distance_unit:
        raise ValidationError(_("Must specify a unit when setting a distance"))


_distance_mixin_models = [
    'circuits.circuit',
    'wireless.wirelesslink',
]

for _label in _distance_mixin_models:
    validator_registry.register(_label,
        ModelValidator(
            name='distance_unit_required',
            model_label=_label,
            fields=_fs({'distance', 'distance_unit'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_distance_unit_required,
            description='Distance requires a unit',
        ),
    )


# ──────────────────────────────────────────────────────────────────────
# NestedGroupModel — MPTT parent cycle check
# ──────────────────────────────────────────────────────────────────────

def validate_nested_group_parent(instance):
    if not instance._state.adding and instance.parent and instance.parent in instance.get_descendants(include_self=True):
        raise ValidationError({
            "parent": "Cannot assign self or child {type} as parent.".format(type=instance._meta.verbose_name)
        })


_nested_group_models = [
    'dcim.region',
    'dcim.sitegroup',
    'dcim.location',
    'dcim.devicerole',
    'dcim.platform',
    'tenancy.tenantgroup',
    'tenancy.contactgroup',
    'wireless.wirelesslangroup',
]

for _label in _nested_group_models:
    validator_registry.register(_label,
        ModelValidator(
            name='nested_group_parent_cycle',
            model_label=_label,
            fields=_fs({'parent'}),
            category=ValidatorCategory.CROSS_MODEL,
            validate=validate_nested_group_parent,
            description='MPTT model cannot be its own parent or descendant',
        ),
    )


# ──────────────────────────────────────────────────────────────────────
# ModuleType — jsonschema attribute validation
# ──────────────────────────────────────────────────────────────────────

def validate_moduletype_attributes(instance):
    import jsonschema as _jsonschema
    from jsonschema.exceptions import ValidationError as JSONValidationError
    if instance.profile and instance.profile.schema:
        try:
            _jsonschema.validate(instance.attribute_data, schema=instance.profile.schema)
        except JSONValidationError as e:
            raise ValidationError(_("Invalid schema: {error}").format(error=e))
    else:
        instance.attribute_data = None


validator_registry.register('dcim.moduletype',
    ModelValidator(
        name='moduletype_attribute_schema',
        model_label='dcim.moduletype',
        fields=_fs({'attribute_data', 'profile'}),
        category=ValidatorCategory.FIELD,
        validate=validate_moduletype_attributes,
        description='Validate attribute_data against profile schema',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# CustomFieldsMixin — sentinel-based registration
#
# Uses the mixin sentinel pattern: a single registration under a
# pseudo-label that automatically applies to every model inheriting
# CustomFieldsMixin (which is every NetBoxModel via NetBoxFeatureSet).
# External tools can query validator_registry.get_validators(
#     '__mixin:CustomFieldsMixin__') to see these rules.
# ──────────────────────────────────────────────────────────────────────

_CF_SENTINEL = '__mixin:CustomFieldsMixin__'


def _get_custom_fields_for(instance):
    """Fetch custom fields applicable to this instance's model (cached per-call)."""
    from extras.models import CustomField
    return {cf.name: cf for cf in CustomField.objects.get_for_model(instance)}


def validate_custom_field_values(instance):
    """Validate each custom field value against its field-level constraints."""
    custom_fields = _get_custom_fields_for(instance)
    for field_name, value in instance.custom_field_data.items():
        if field_name not in custom_fields:
            continue
        try:
            custom_fields[field_name].validate(value)
        except ValidationError as e:
            raise ValidationError(_("Invalid value for custom field '{name}': {error}").format(
                name=field_name, error=e.message
            ))


def validate_custom_field_uniqueness(instance):
    """Enforce uniqueness constraints on custom field values."""
    from extras.constants import CUSTOMFIELD_EMPTY_VALUES
    custom_fields = _get_custom_fields_for(instance)
    for field_name, value in instance.custom_field_data.items():
        cf = custom_fields.get(field_name)
        if cf and cf.unique and value not in CUSTOMFIELD_EMPTY_VALUES:
            if instance._meta.model.objects.exclude(pk=instance.pk).filter(**{
                f'custom_field_data__{field_name}': value
            }).exists():
                raise ValidationError(_("Custom field '{name}' must have a unique value.").format(
                    name=field_name
                ))


def validate_custom_field_required(instance):
    """Ensure all required custom fields have values."""
    custom_fields = _get_custom_fields_for(instance)
    for cf in custom_fields.values():
        if cf.required and cf.name not in instance.custom_field_data:
            raise ValidationError(_("Missing required custom field '{name}'.").format(name=cf.name))


def _normalize_custom_field_data(instance):
    """
    Prune stale CF keys and fill missing defaults in one pass.

    This replaces both the stale-key pruning from clean() and the
    default-filling from save(). Returns the normalized dict.
    """
    from extras.models import CustomField
    custom_fields = {cf.name: cf for cf in CustomField.objects.get_for_model(instance)}
    data = instance.custom_field_data or {}
    normalized = {k: v for k, v in data.items() if k in custom_fields}
    for cf_name, cf in custom_fields.items():
        if cf_name not in normalized and cf.default is not None:
            normalized[cf_name] = cf.default
    return normalized


def _register_cf_sentinel():
    from netbox.denorm import DenormSpec, denorm_registry
    from netbox.models.features import CustomFieldsMixin

    # -- Validator sentinel --
    validator_registry.register_mixin_sentinel(_CF_SENTINEL, CustomFieldsMixin)
    validator_registry.register(
        _CF_SENTINEL,
        ModelValidator(
            name='cf_validate_values',
            model_label=_CF_SENTINEL,
            fields=_fs({'custom_field_data'}),
            category=ValidatorCategory.FIELD,
            validate=validate_custom_field_values,
            queries_db=True,
            description='Validate each custom field value against its type/constraints',
        ),
        ModelValidator(
            name='cf_validate_uniqueness',
            model_label=_CF_SENTINEL,
            fields=_fs({'custom_field_data'}),
            category=ValidatorCategory.UNIQUENESS,
            validate=validate_custom_field_uniqueness,
            queries_db=True,
            description='Enforce uniqueness on custom fields marked unique',
        ),
        ModelValidator(
            name='cf_validate_required',
            model_label=_CF_SENTINEL,
            fields=_fs({'custom_field_data'}),
            category=ValidatorCategory.CROSS_FIELD,
            validate=validate_custom_field_required,
            queries_db=True,
            description='Ensure all required custom fields are present',
        ),
    )

    # -- Denorm sentinel --
    denorm_registry.register_mixin_sentinel(_CF_SENTINEL, CustomFieldsMixin)
    denorm_registry.register(
        _CF_SENTINEL,
        DenormSpec(
            field_name='custom_field_data',
            compute=_normalize_custom_field_data,
            depends_on=_fs({'custom_field_data'}),
        ),
    )


_register_cf_sentinel()
