import logging
from datetime import datetime
from decimal import Decimal

from django.core.exceptions import NON_FIELD_ERRORS, FieldDoesNotExist, ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from utilities.exceptions import AbortRequest, PermissionsViolation
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'UNEXPECTED_ERROR',
    'coerce_values',
    'enforce_object_permission',
    'find_manufacturer',
    'get_error_message',
    'get_or_create_manufacturer',
    'parse_strict_date',
    'save_form',
    'upsert',
)

logger = logging.getLogger('netbox.ndx.importers')

# Reported in place of the details of an unexpected error, which are logged instead
UNEXPECTED_ERROR = _("An unexpected error occurred; see the NetBox log for details.")


def _get_form_value(field, instance, name):
    value = getattr(instance, name, None)
    if hasattr(value, 'all'):
        value = list(value.all())
    return field.prepare_value(value)


def _bind_form(form_class, data, instance, user):
    supplied = set(data)

    # When updating an object, leave fields which were not supplied unchanged. Model fields are populated from the
    # instance (rather than removed) because form validation may reference them.
    if instance.pk:
        model_fields = set(form_class._meta.fields or ())
        unbound_fields = form_class(instance=instance).fields
        data = {
            **{
                name: _get_form_value(field, instance, name)
                for name, field in unbound_fields.items() if name not in data and name in model_fields
            },
            **data,
        }
    form = form_class(data=data, instance=instance)
    if instance.pk:
        for name in [name for name in form.fields if name not in data]:
            del form.fields[name]
    # Limit the objects which may be referenced by supplied values to those the user can view
    if user is not None:
        for name, field in form.fields.items():
            if name in supplied and isinstance(getattr(field, 'queryset', None), RestrictedQuerySet):
                field.queryset = field.queryset.restrict(user, 'view')
    return form


def _fill_initial_values(form_class, data):
    # Mirror BulkImportView: omitted fields take their initial values (e.g. model and custom field defaults)
    for name, field in form_class().fields.items():
        if name not in data and field.initial is not None and not callable(field.initial):
            data[name] = field.initial


def _format_errors(form):
    return '; '.join(
        f'{name}: {" ".join(messages)}' if name != NON_FIELD_ERRORS else ' '.join(messages)
        for name, messages in form.errors.items()
    )


def _quantize_decimals(instance):
    # Match the precision with which decimal values are stored, so that an unchanged value (e.g. 1 for a stored 1.0)
    # isn't recorded as a change
    for field in instance._meta.concrete_fields:
        if isinstance(field, models.DecimalField) and isinstance(value := getattr(instance, field.attname), Decimal):
            setattr(instance, field.attname, value.quantize(Decimal(1).scaleb(-field.decimal_places)))


def _save(form, original, supplied):
    instance = form.instance
    # Restore any fields which were not supplied. Their values pass through the form only for validation, which may
    # not preserve their representation (e.g. an empty string in place of null).
    for field in instance._meta.concrete_fields:
        if field.name in original and field.name not in supplied:
            setattr(instance, field.attname, original[field.name])
    _quantize_decimals(instance)
    return form.save()


def save_form(form_class, data, instance, *, user=None, protected=(), warnings=None, label=''):
    """
    Validate catalog data through a NetBox import form and save the resulting object.

    A value which the form rejects for any field not listed in `protected` is replaced (with "other" for a
    required choice field, or else by leaving the field unchanged/at its default) and the substitution is
    appended to `warnings`. Raises ValidationError if the data cannot be validated.
    """
    data = {k: v for k, v in data.items() if v is not None}
    original = {}
    if instance.pk:
        instance.snapshot()
        form_fields = set(form_class._meta.fields or ())
        original = {
            field.name: getattr(instance, field.attname)
            for field in instance._meta.concrete_fields if field.name in form_fields
        }
    else:
        _fill_initial_values(form_class, data)

    form = _bind_form(form_class, data, instance, user)
    if form.is_valid():
        return _save(form, original, set(data))

    rejected = [name for name in form.errors if name in data and name not in protected]
    if len(rejected) != len(form.errors):
        raise ValidationError(_format_errors(form))

    for name in rejected:
        value = data.pop(name)
        field = form.fields[name]
        if field.required and hasattr(field, 'valid_value') and field.valid_value('other'):
            data[name] = 'other'
        elif not instance.pk and field.initial is not None:
            data[name] = field.initial
        msg = f"{label}: rejected {name} {value!r} ({' '.join(form.errors[name])})"
        logger.warning(msg)
        if warnings is not None:
            warnings.append(msg)

    form = _bind_form(form_class, data, instance, user)
    if not form.is_valid():
        raise ValidationError(_format_errors(form))
    return _save(form, original, set(data))


def coerce_values(model, values, warnings=None):
    """
    Convert catalog values to the Python types of the given model's fields. A value which cannot be converted (or
    which fails the field's validators, e.g. for maximum length or range) is replaced with the field's default.
    """
    coerced = {}
    for name, value in values.items():
        try:
            field = model._meta.get_field(name)
        except FieldDoesNotExist:
            coerced[name] = value
            continue
        if field.is_relation:
            coerced[name] = value
            continue
        try:
            # Discard the time portion of a timestamp supplied for a date field
            if type(field) is models.DateField and isinstance(value, str):
                value = value.split('T')[0]
            value = field.to_python(value)
            if value is None and not field.null:
                value = field.get_default()
            field.run_validators(value)
        except ValidationError as e:
            msg = f"{model._meta.verbose_name}: rejected {name} {value!r} ({' '.join(e.messages)})"
            logger.warning(msg)
            if warnings is not None:
                warnings.append(msg)
            value = field.get_default()
        coerced[name] = value
    return coerced


def upsert(model, lookup, values, warnings=None):
    """
    Create or update an object matching `lookup`, recording a pre-change snapshot for updates.
    """
    values = coerce_values(model, values, warnings)
    instance = model.objects.filter(**lookup).first()
    if instance is None:
        instance = model(**lookup, **values)
        instance.full_clean(validate_unique=False, validate_constraints=False)
        instance.save()
        return instance, True

    instance.snapshot()
    for name, value in values.items():
        setattr(instance, name, value)
    instance.full_clean(validate_unique=False, validate_constraints=False)
    instance.save()
    return instance, False


def get_error_message(exc):
    """
    Return a message describing an error for reporting. The details of an unexpected error are not reported.
    """
    if isinstance(exc, (AbortRequest, ValidationError)):
        return '; '.join(getattr(exc, 'messages', None) or [str(exc)])
    logger.error(f"Unexpected error during import: {exc!r}")
    return str(UNEXPECTED_ERROR)


def enforce_object_permission(obj, user, action):
    """
    Raise PermissionsViolation if the user's object-level permissions don't permit the given action on a saved object.
    """
    model = type(obj)
    if getattr(model, '_netbox_private', False):
        return
    if not model.objects.restrict(user, action).filter(pk=obj.pk).exists():
        raise PermissionsViolation()


def get_or_create_manufacturer(name):
    """
    Return the manufacturer matching the given name by slug or (case-insensitive) name, creating it if necessary.
    """
    from dcim.models import Manufacturer

    if manufacturer := find_manufacturer(name):
        return manufacturer
    manufacturer = Manufacturer(name=name, slug=slugify(name))
    manufacturer.full_clean()
    manufacturer.save()
    return manufacturer


def find_manufacturer(name):
    """
    Return the existing manufacturer matching the given name by slug or (case-insensitive) name, if any.
    """
    from dcim.models import Manufacturer

    if not name:
        return None
    return (
        Manufacturer.objects.filter(slug=slugify(name)).first() or
        Manufacturer.objects.filter(name__iexact=name).first()
    )


def parse_strict_date(value):
    """
    Parse a YYYY-MM-DD string to a date. Returns None for any other value (including partial dates).
    """
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None
