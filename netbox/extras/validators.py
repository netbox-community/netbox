import importlib

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# NOTE: As this module may be imported by configuration.py, we cannot import
# anything from NetBox itself.


class IsEqualValidator(validators.BaseValidator):
    """
    Employed by CustomValidator to require a specific value.
    """
    message = _("Ensure this value is equal to %(limit_value)s.")
    code = "is_equal"

    def compare(self, a, b):
        return a != b


class IsNotEqualValidator(validators.BaseValidator):
    """
    Employed by CustomValidator to exclude a specific value.
    """
    message = _("Ensure this value does not equal %(limit_value)s.")
    code = "is_not_equal"

    def compare(self, a, b):
        return a == b


class IsEmptyValidator:
    """
    Employed by CustomValidator to enforce required fields.
    """
    message = _("This field must be empty.")
    code = 'is_empty'

    def __init__(self, enforce=True):
        self._enforce = enforce

    def __call__(self, value):
        if self._enforce and value not in validators.EMPTY_VALUES:
            raise ValidationError(self.message, code=self.code)


class IsNotEmptyValidator:
    """
    Employed by CustomValidator to enforce prohibited fields.
    """
    message = _("This field must not be empty.")
    code = 'not_empty'

    def __init__(self, enforce=True):
        self._enforce = enforce

    def __call__(self, value):
        if self._enforce and value in validators.EMPTY_VALUES:
            raise ValidationError(self.message, code=self.code)


class CustomValidator:
    """
    This class enables the application of user-defined validation rules to NetBox models. It can be instantiated by
    passing a dictionary of validation rules in the form {attribute: rules}, where 'rules' is a dictionary mapping
    descriptors (e.g. min_length or regex) to values.

    A CustomValidator instance is applied by calling it with the instance being validated:

        validator = CustomValidator({'name': {'min_length: 10}})
        site = Site(name='abcdef')
        validator(site)  # Raises ValidationError

    :param validation_rules: A dictionary mapping object attributes to validation rules
    """
    VALIDATORS = {
        'eq': IsEqualValidator,
        'neq': IsNotEqualValidator,
        'min': validators.MinValueValidator,
        'max': validators.MaxValueValidator,
        'min_length': validators.MinLengthValidator,
        'max_length': validators.MaxLengthValidator,
        'regex': validators.RegexValidator,
        'required': IsNotEmptyValidator,
        'prohibited': IsEmptyValidator,
    }

    def __init__(self, validation_rules=None):
        self.validation_rules = validation_rules or {}
        assert type(self.validation_rules) is dict, "Validation rules must be passed as a dictionary"

    def __call__(self, instance):
        # Validate instance attributes per validation rules
        for attr_name, rules in self.validation_rules.items():
            attr = self._getattr(instance, attr_name)
            for descriptor, value in rules.items():
                validator = self.get_validator(descriptor, value)
                try:
                    validator(attr)
                except ValidationError as exc:
                    # Re-package the raised ValidationError to associate it with the specific attr
                    raise ValidationError({attr_name: exc})

        # Execute custom validation logic (if any)
        self.validate(instance)

    @staticmethod
    def _getattr(instance, name):
        # Attempt to resolve many-to-many fields to their stored values
        m2m_fields = [f.name for f in instance._meta.local_many_to_many]
        if name in m2m_fields:
            if name in getattr(instance, '_m2m_values', []):
                return instance._m2m_values[name]
            if instance.pk:
                return list(getattr(instance, name).all())
            return []

        # Raise a ValidationError for unknown attributes
        if not hasattr(instance, name):
            raise ValidationError(_('Invalid attribute "{name}" for {model}').format(
                name=name,
                model=instance.__class__.__name__
            ))

        return getattr(instance, name)

    def get_validator(self, descriptor, value):
        """
        Instantiate and return the appropriate validator based on the descriptor given. For
        example, 'min' returns MinValueValidator(value).
        """
        if descriptor not in self.VALIDATORS:
            raise NotImplementedError(
                f"Unknown validation type for {self.__class__.__name__}: '{descriptor}'"
            )
        validator_cls = self.VALIDATORS.get(descriptor)
        return validator_cls(value)

    def validate(self, instance):
        """
        Custom validation method, to be overridden by the user. Validation failures should
        raise a ValidationError exception.
        """
        return

    def fail(self, message, field=None):
        """
        Raise a ValidationError exception. Associate the provided message with a form/serializer field if specified.
        """
        if field is not None:
            raise ValidationError({field: message})
        raise ValidationError(message)


def run_validators(instance, validators):
    """
    Run the provided iterable of validators for the instance.
    """
    for validator in validators:

        # Loading a validator class by dotted path
        if type(validator) is str:
            module, cls = validator.rsplit('.', 1)
            validator = getattr(importlib.import_module(module), cls)()

        # Constructing a new instance on the fly from a ruleset
        elif type(validator) is dict:
            validator = CustomValidator(validator)

        validator(instance)
