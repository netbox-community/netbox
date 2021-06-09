from django.core.exceptions import ValidationError
from django.core import validators

# NOTE: As this module may be imported by configuration.py, we cannot import
# anything from NetBox itself.


class IsEmptyValidator:
    """
    Employed by CustomValidator to enforce required fields.
    """
    message = "This field must be empty."
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
    message = "This field must not be empty."
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
            assert hasattr(instance, attr_name), f"Invalid attribute '{attr_name}' for {instance.__class__.__name__}"
            attr = getattr(instance, attr_name)
            for descriptor, value in rules.items():
                validator = self.get_validator(descriptor, value)
                try:
                    validator(attr)
                except ValidationError as exc:
                    # Re-package the raised ValidationError to associate it with the specific attr
                    raise ValidationError({attr_name: exc})

        # Execute custom validation logic (if any)
        self.validate(instance)

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
