from dataclasses import dataclass
from enum import Enum
from typing import Any

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.validators import RegexValidator

from utilities.string import title
from utilities.validators import MultipleOfValidator

__all__ = (
    'JSONSchemaProperty',
    'PropertyTypeEnum',
    'StringFormatEnum',
)


class PropertyTypeEnum(Enum):
    STRING = 'string'
    INTEGER = 'integer'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    OBJECT = 'object'


class StringFormatEnum(Enum):
    EMAIL = 'email'
    URI = 'uri'
    IRI = 'iri'
    UUID = 'uuid'
    DATE = 'date'
    TIME = 'time'
    DATETIME = 'datetime'


FORM_FIELDS = {
    PropertyTypeEnum.STRING.value: forms.CharField,
    PropertyTypeEnum.INTEGER.value: forms.IntegerField,
    PropertyTypeEnum.NUMBER.value: forms.FloatField,
    PropertyTypeEnum.BOOLEAN.value: forms.BooleanField,
    PropertyTypeEnum.ARRAY.value: SimpleArrayField,
    PropertyTypeEnum.OBJECT.value: forms.JSONField,
}

STRING_FORM_FIELDS = {
    StringFormatEnum.EMAIL.value: forms.EmailField,
    StringFormatEnum.URI.value: forms.URLField,
    StringFormatEnum.IRI.value: forms.URLField,
    StringFormatEnum.UUID.value: forms.UUIDField,
    StringFormatEnum.DATE.value: forms.DateField,
    StringFormatEnum.TIME.value: forms.TimeField,
    StringFormatEnum.DATETIME.value: forms.DateTimeField,
}


@dataclass
class JSONSchemaProperty:
    type: PropertyTypeEnum = PropertyTypeEnum.STRING.value
    title: str | None = None
    description: str | None = None
    default: Any = None
    enum: list | None = None

    # Strings
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = None  # Regex
    format: StringFormatEnum | None = None

    # Numbers
    minimum: int | float | None = None
    maximum: int | float | None = None
    multipleOf: int | float | None = None

    def to_form_field(self, name, required=False):
        """
        Instantiate and return a Django form field suitable for editing the property's value.
        """
        field_kwargs = {
            'label': self.title or title(name),
            'help_text': self.description,
            'required': required,
            'initial': self.default,
        }

        # Choices
        if self.enum:
            choices = [(v, v) for v in self.enum]
            if not required:
                choices = [(None, ''), *choices]
            field_kwargs['choices'] = choices

        # String validation
        if self.type == PropertyTypeEnum.STRING.value:
            if self.minLength is not None:
                field_kwargs['min_length'] = self.minLength
            if self.maxLength is not None:
                field_kwargs['max_length'] = self.maxLength
            if self.pattern is not None:
                field_kwargs['validators'] = [
                    RegexValidator(regex=self.pattern)
                ]

        # Integer/number validation
        elif self.type in (PropertyTypeEnum.INTEGER.value, PropertyTypeEnum.NUMBER.value):
            field_kwargs['widget'] = forms.NumberInput(attrs={'step': 'any'})
            if self.minimum:
                field_kwargs['min_value'] = self.minimum
            if self.maximum:
                field_kwargs['max_value'] = self.maximum
            if self.multipleOf:
                field_kwargs['validators'] = [
                    MultipleOfValidator(multiple=self.multipleOf)
                ]
        return self.field_class(**field_kwargs)

    @property
    def field_class(self):
        """
        Resolve the property's type (and string format, if specified) to the appropriate field class.
        """
        if self.enum:
            if self.type == PropertyTypeEnum.ARRAY.value:
                return forms.MultipleChoiceField
            return forms.ChoiceField
        if self.type == PropertyTypeEnum.STRING.value and self.format is not None:
            try:
                return STRING_FORM_FIELDS[self.format]
            except KeyError:
                raise ValueError(f"Unsupported string format type: {self.format}")
        try:
            return FORM_FIELDS[self.type]
        except KeyError:
            raise ValueError(f"Unknown property type: {self.type}")
