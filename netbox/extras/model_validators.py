"""
Extracted, composable validators for extras models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# CustomField
# ──────────────────────────────────────────────────────────────────────

def validate_cf_default(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.default is not None:
        try:
            if instance.type in (CustomFieldTypeChoices.TYPE_TEXT, CustomFieldTypeChoices.TYPE_LONGTEXT):
                default_value = str(instance.default)
            else:
                default_value = instance.default
            instance.validate(default_value)
        except ValidationError as err:
            raise ValidationError({
                'default': _(
                    'Invalid default value "{value}": {error}'
                ).format(value=instance.default, error=err.message)
            })


def validate_cf_numeric_constraints(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.type not in (CustomFieldTypeChoices.TYPE_INTEGER, CustomFieldTypeChoices.TYPE_DECIMAL):
        if instance.validation_minimum:
            raise ValidationError({'validation_minimum': _("A minimum value may be set only for numeric fields")})
        if instance.validation_maximum:
            raise ValidationError({'validation_maximum': _("A maximum value may be set only for numeric fields")})


def validate_cf_regex_type(instance):
    from extras.choices import CustomFieldTypeChoices
    regex_types = (
        CustomFieldTypeChoices.TYPE_TEXT,
        CustomFieldTypeChoices.TYPE_LONGTEXT,
        CustomFieldTypeChoices.TYPE_URL,
    )
    if instance.validation_regex and instance.type not in regex_types:
        raise ValidationError({
            'validation_regex': _("Regular expression validation is supported only for text and URL fields")
        })


def validate_cf_unique_boolean(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.unique and instance.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
        raise ValidationError({
            'unique': _("Uniqueness cannot be enforced for boolean fields")
        })


def validate_cf_choice_set(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.type in (
            CustomFieldTypeChoices.TYPE_SELECT,
            CustomFieldTypeChoices.TYPE_MULTISELECT
    ):
        if not instance.choice_set:
            raise ValidationError({
                'choice_set': _("Selection fields must specify a set of choices.")
            })
    elif instance.choice_set:
        raise ValidationError({
            'choice_set': _("Choices may be set only on selection fields.")
        })


def validate_cf_object_type(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.type in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT):
        if not instance.related_object_type:
            raise ValidationError({
                'related_object_type': _("Object fields must define an object type.")
            })
    elif instance.related_object_type:
        raise ValidationError({
            'type': _("{type} fields may not define an object type.").format(type=instance.get_type_display())
        })


def validate_cf_object_filter(instance):
    from extras.choices import CustomFieldTypeChoices
    if instance.related_object_filter is not None:
        if instance.type not in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT):
            raise ValidationError({
                'related_object_filter': _("A related object filter can be defined only for object fields.")
            })
        if type(instance.related_object_filter) is not dict:
            raise ValidationError({
                'related_object_filter': _("Filter must be defined as a dictionary mapping attributes to values.")
            })


validator_registry.register('extras.customfield',
    ModelValidator(
        name='cf_default',
        model_label='extras.customfield',
        fields=_fs({'default', 'type'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_default,
        description='Default value must be valid for field type',
    ),
    ModelValidator(
        name='cf_numeric_constraints',
        model_label='extras.customfield',
        fields=_fs({'type', 'validation_minimum', 'validation_maximum'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_numeric_constraints,
        description='Min/max values only for numeric fields',
    ),
    ModelValidator(
        name='cf_regex_type',
        model_label='extras.customfield',
        fields=_fs({'type', 'validation_regex'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_regex_type,
        description='Regex validation only for text/URL fields',
    ),
    ModelValidator(
        name='cf_unique_boolean',
        model_label='extras.customfield',
        fields=_fs({'type', 'unique'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_unique_boolean,
        description='Uniqueness cannot be enforced for booleans',
    ),
    ModelValidator(
        name='cf_choice_set',
        model_label='extras.customfield',
        fields=_fs({'type', 'choice_set'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_choice_set,
        description='Choice set required for selection fields only',
    ),
    ModelValidator(
        name='cf_object_type',
        model_label='extras.customfield',
        fields=_fs({'type', 'related_object_type'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_object_type,
        description='Object type required for object fields only',
    ),
    ModelValidator(
        name='cf_object_filter',
        model_label='extras.customfield',
        fields=_fs({'type', 'related_object_filter'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cf_object_filter,
        description='Object filter only for object fields and must be dict',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CustomFieldChoiceSet
# ──────────────────────────────────────────────────────────────────────

def validate_cfchoiceset_has_choices(instance):
    if not instance.base_choices and not instance.extra_choices:
        raise ValidationError(_("Must define base or extra choices."))


def validate_cfchoiceset_duplicate_values(instance):
    choice_values = [c[0] for c in instance.extra_choices] if instance.extra_choices else []
    if len(set(choice_values)) != len(choice_values):
        _seen = []
        for value in choice_values:
            if value in _seen:
                raise ValidationError(_("Duplicate value '{value}' found in extra choices.").format(value=value))
            _seen.append(value)


def validate_cfchoiceset_removed_in_use(instance):
    from extras.choices import CustomFieldTypeChoices
    original_choices = set([
        c[0] for c in instance._original_extra_choices
    ]) if instance._original_extra_choices else set()
    current_choices = set([
        c[0] for c in instance.extra_choices
    ]) if instance.extra_choices else set()
    if removed_choices := original_choices - current_choices:
        for custom_field in instance.choices_for.all():
            for object_type in custom_field.object_types.all():
                model = object_type.model_class()
                for choice in removed_choices:
                    if custom_field.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
                        query_args = {f"custom_field_data__{custom_field.name}__contains": choice}
                    else:
                        query_args = {f"custom_field_data__{custom_field.name}": choice}
                    from django.db import models as db_models
                    if model.objects.filter(db_models.Q(**query_args)).exists():
                        raise ValidationError(
                            _(
                                "Cannot remove choice {choice} as there are {model} objects which reference it."
                            ).format(choice=choice, model=object_type)
                        )


validator_registry.register('extras.customfieldchoiceset',
    ModelValidator(
        name='cfchoiceset_has_choices',
        model_label='extras.customfieldchoiceset',
        fields=_fs({'base_choices', 'extra_choices'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_cfchoiceset_has_choices,
        description='Must define base or extra choices',
    ),
    ModelValidator(
        name='cfchoiceset_duplicate_values',
        model_label='extras.customfieldchoiceset',
        fields=_fs({'extra_choices'}),
        category=ValidatorCategory.FIELD,
        validate=validate_cfchoiceset_duplicate_values,
        description='No duplicate values in extra choices',
    ),
    ModelValidator(
        name='cfchoiceset_removed_in_use',
        model_label='extras.customfieldchoiceset',
        fields=_fs({'extra_choices'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cfchoiceset_removed_in_use,
        queries_db=True,
        description='Cannot remove choices still referenced by objects',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# TableConfig
# ──────────────────────────────────────────────────────────────────────

def validate_tableconfig_table_class(instance):
    if instance.table_class is None:
        raise ValidationError({
            'table': _("Unknown table: {name}").format(name=instance.table)
        })


def validate_tableconfig_columns(instance):
    if instance.table_class is None:
        return
    table = instance.table_class([])
    for name in instance.ordering:
        col_name = name.lstrip('-')
        if col_name not in table.columns:
            raise ValidationError({
                'ordering': _('Unknown column: {name}').format(name=col_name)
            })
    for name in instance.columns:
        if name not in table.columns:
            raise ValidationError({
                'columns': _('Unknown column: {name}').format(name=name)
            })


validator_registry.register('extras.tableconfig',
    ModelValidator(
        name='tableconfig_table_class',
        model_label='extras.tableconfig',
        fields=_fs({'table', 'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_tableconfig_table_class,
        description='Table class must exist',
    ),
    ModelValidator(
        name='tableconfig_columns',
        model_label='extras.tableconfig',
        fields=_fs({'table', 'object_type', 'columns', 'ordering'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_tableconfig_columns,
        description='Column and ordering names must be valid for the table',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ConfigContext
# ──────────────────────────────────────────────────────────────────────

def validate_configcontext_data_type(instance):
    if type(instance.data) is not dict:
        raise ValidationError(
            {'data': _('JSON data must be in object form. Example:') + ' {"foo": 123}'}
        )


def validate_configcontext_schema(instance):
    if instance.profile and instance.profile.schema:
        import jsonschema
        from jsonschema.exceptions import ValidationError as JSONValidationError
        try:
            jsonschema.validate(instance.data, schema=instance.profile.schema)
        except JSONValidationError as e:
            raise ValidationError(_("Data does not conform to profile schema: {error}").format(error=e))


validator_registry.register('extras.configcontext',
    ModelValidator(
        name='configcontext_data_type',
        model_label='extras.configcontext',
        fields=_fs({'data'}),
        category=ValidatorCategory.FIELD,
        validate=validate_configcontext_data_type,
        description='Config context data must be a JSON object',
    ),
    ModelValidator(
        name='configcontext_schema',
        model_label='extras.configcontext',
        fields=_fs({'data', 'profile'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_configcontext_schema,
        description='Config data must conform to profile schema',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# EventRule
# ──────────────────────────────────────────────────────────────────────

def validate_eventrule_conditions(instance):
    from extras.conditions import ConditionSet
    if instance.conditions:
        try:
            ConditionSet(instance.conditions)
        except ValueError as e:
            raise ValidationError({'conditions': e})


validator_registry.register('extras.eventrule',
    ModelValidator(
        name='eventrule_conditions',
        model_label='extras.eventrule',
        fields=_fs({'conditions'}),
        category=ValidatorCategory.FIELD,
        validate=validate_eventrule_conditions,
        description='Conditions must be valid ConditionSet format',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Webhook
# ──────────────────────────────────────────────────────────────────────

def validate_webhook_ssl_ca(instance):
    if not instance.ssl_verification and instance.ca_file_path:
        raise ValidationError({
            'ca_file_path': _('Do not specify a CA certificate file if SSL verification is disabled.')
        })


validator_registry.register('extras.webhook',
    ModelValidator(
        name='webhook_ssl_ca',
        model_label='extras.webhook',
        fields=_fs({'ssl_verification', 'ca_file_path'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_webhook_ssl_ca,
        description='CA file path requires SSL verification enabled',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ExportTemplate
# ──────────────────────────────────────────────────────────────────────

def validate_exporttemplate_name(instance):
    if instance.name.lower() == 'table':
        raise ValidationError({
            'name': _('"{name}" is a reserved name. Please choose a different name.').format(name=instance.name)
        })


validator_registry.register('extras.exporttemplate',
    ModelValidator(
        name='exporttemplate_name',
        model_label='extras.exporttemplate',
        fields=_fs({'name'}),
        category=ValidatorCategory.FIELD,
        validate=validate_exporttemplate_name,
        description='Export template name cannot be reserved word "table"',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# SavedFilter
# ──────────────────────────────────────────────────────────────────────

def validate_savedfilter_parameters(instance):
    if type(instance.parameters) is not dict:
        raise ValidationError(
            {'parameters': _('Filter parameters must be stored as a dictionary of keyword arguments.')}
        )


validator_registry.register('extras.savedfilter',
    ModelValidator(
        name='savedfilter_parameters',
        model_label='extras.savedfilter',
        fields=_fs({'parameters'}),
        category=ValidatorCategory.FIELD,
        validate=validate_savedfilter_parameters,
        description='Parameters must be a dict',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ImageAttachment
# ──────────────────────────────────────────────────────────────────────

def validate_imageattachment_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.object_type, 'image_attachments'):
        raise ValidationError(
            _("Image attachments cannot be assigned to this object type ({type}).").format(type=instance.object_type)
        )


validator_registry.register('extras.imageattachment',
    ModelValidator(
        name='imageattachment_feature',
        model_label='extras.imageattachment',
        fields=_fs({'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_imageattachment_feature,
        description='Object type must support image attachments',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# JournalEntry
# ──────────────────────────────────────────────────────────────────────

def validate_journalentry_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.assigned_object_type, 'journaling'):
        raise ValidationError(
            _("Journaling is not supported for this object type ({type}).").format(type=instance.assigned_object_type)
        )


validator_registry.register('extras.journalentry',
    ModelValidator(
        name='journalentry_feature',
        model_label='extras.journalentry',
        fields=_fs({'assigned_object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_journalentry_feature,
        description='Object type must support journaling',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Bookmark
# ──────────────────────────────────────────────────────────────────────

def validate_bookmark_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.object_type, 'bookmarks'):
        raise ValidationError(
            _("Bookmarks cannot be assigned to this object type ({type}).").format(type=instance.object_type)
        )


validator_registry.register('extras.bookmark',
    ModelValidator(
        name='bookmark_feature',
        model_label='extras.bookmark',
        fields=_fs({'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_bookmark_feature,
        description='Object type must support bookmarks',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Notification
# ──────────────────────────────────────────────────────────────────────

def validate_notification_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.object_type, 'notifications'):
        raise ValidationError(
            _("Objects of this type ({type}) do not support notifications.").format(type=instance.object_type)
        )


validator_registry.register('extras.notification',
    ModelValidator(
        name='notification_feature',
        model_label='extras.notification',
        fields=_fs({'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_notification_feature,
        description='Object type must support notifications',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Subscription
# ──────────────────────────────────────────────────────────────────────

def validate_subscription_feature(instance):
    from netbox.models.features import has_feature
    if not has_feature(instance.object_type, 'notifications'):
        raise ValidationError(
            _("Objects of this type ({type}) do not support notifications.").format(type=instance.object_type)
        )


validator_registry.register('extras.subscription',
    ModelValidator(
        name='subscription_feature',
        model_label='extras.subscription',
        fields=_fs({'object_type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_subscription_feature,
        description='Object type must support notifications',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ConfigContextModel (abstract — register for each concrete model)
# ──────────────────────────────────────────────────────────────────────

def validate_configcontextmodel_local_context_data(instance):
    if instance.local_context_data is not None and type(instance.local_context_data) is not dict:
        raise ValidationError(
            {'local_context_data': _('JSON data must be in object form. Example:') + ' {"foo": 123}'}
        )


_configcontextmodel_validators = [
    ModelValidator(
        name='configcontextmodel_local_context_data',
        model_label='',
        fields=_fs({'local_context_data'}),
        category=ValidatorCategory.FIELD,
        validate=validate_configcontextmodel_local_context_data,
        description='Local context data must be a dict if provided',
    ),
]

for _label in ('dcim.device', 'virtualization.virtualmachine'):
    validator_registry.register(_label, *_configcontextmodel_validators)
