from collections import OrderedDict

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.utils.safestring import mark_safe

from utilities.forms import CSVChoiceField, DatePicker, LaxURLField, StaticSelect2, add_blank_choice
from utilities.validators import validate_regex
from extras.choices import *
from extras.utils import FeatureQuery


class CustomFieldModel(models.Model):
    """
    Abstract class for any model which may have custom fields associated with it.
    """
    custom_field_data = models.JSONField(
        encoder=DjangoJSONEncoder,
        blank=True,
        default=dict
    )

    class Meta:
        abstract = True

    @property
    def cf(self):
        """
        Convenience wrapper for custom field data.
        """
        return self.custom_field_data

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form {<field>: value}.
        """
        fields = CustomField.objects.get_for_model(self)
        return OrderedDict([
            (field, self.custom_field_data.get(field.name)) for field in fields
        ])


class CustomFieldManager(models.Manager):
    use_in_migrations = True

    def get_for_model(self, model):
        """
        Return all CustomFields assigned to the given model.
        """
        content_type = ContentType.objects.get_for_model(model._meta.concrete_model)
        return self.get_queryset().filter(content_types=content_type)


class CustomField(models.Model):
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='custom_fields',
        verbose_name='Object(s)',
        limit_choices_to=FeatureQuery('custom_fields'),
        help_text='The object(s) to which this field applies.'
    )
    type = models.CharField(
        max_length=50,
        choices=CustomFieldTypeChoices,
        default=CustomFieldTypeChoices.TYPE_TEXT
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Internal field name'
    )
    label = models.CharField(
        max_length=50,
        blank=True,
        help_text='Name of the field as displayed to users (if not provided, '
                  'the field\'s name will be used)'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    required = models.BooleanField(
        default=False,
        help_text='If true, this field is required when creating new objects '
                  'or editing an existing object.'
    )
    filter_logic = models.CharField(
        max_length=50,
        choices=CustomFieldFilterLogicChoices,
        default=CustomFieldFilterLogicChoices.FILTER_LOOSE,
        help_text='Loose matches any instance of a given string; exact '
                  'matches the entire field.'
    )
    default = models.CharField(
        max_length=100,
        blank=True,
        help_text='Default value for the field. Use "true" or "false" for booleans.'
    )
    weight = models.PositiveSmallIntegerField(
        default=100,
        help_text='Fields with higher weights appear lower in a form.'
    )
    validation_minimum = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Minimum value',
        help_text='Minimum allowed value (for numeric fields)'
    )
    validation_maximum = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Maximum value',
        help_text='Maximum allowed value (for numeric fields)'
    )
    validation_regex = models.CharField(
        blank=True,
        validators=[validate_regex],
        max_length=500,
        verbose_name='Validation regex',
        help_text='Regular expression to enforce on text field values. Use ^ and $ to force matching of entire string. '
                  'For example, <code>^[A-Z]{3}$</code> will limit values to exactly three uppercase letters.'
    )
    choices = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        null=True,
        help_text='Comma-separated list of available choices (for selection fields)'
    )

    objects = CustomFieldManager()

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.label or self.name.replace('_', ' ').capitalize()

    def remove_stale_data(self, content_types):
        """
        Delete custom field data which is no longer relevant (either because the CustomField is
        no longer assigned to a model, or because it has been deleted).
        """
        for ct in content_types:
            model = ct.model_class()
            for obj in model.objects.filter(**{f'custom_field_data__{self.name}__isnull': False}):
                del(obj.custom_field_data[self.name])
                obj.save()

    def clean(self):
        # Minimum/maximum values can be set only for numeric fields
        if self.validation_minimum is not None and self.type != CustomFieldTypeChoices.TYPE_INTEGER:
            raise ValidationError({
                'validation_minimum': "A minimum value may be set only for numeric fields"
            })
        if self.validation_maximum is not None and self.type != CustomFieldTypeChoices.TYPE_INTEGER:
            raise ValidationError({
                'validation_maximum': "A maximum value may be set only for numeric fields"
            })

        # Regex validation can be set only for text fields
        if self.validation_regex and self.type != CustomFieldTypeChoices.TYPE_TEXT:
            raise ValidationError({
                'validation_regex': "Regular expression validation is supported only for text and URL fields"
            })

        # Choices can be set only on selection fields
        if self.choices and self.type != CustomFieldTypeChoices.TYPE_SELECT:
            raise ValidationError({
                'choices': "Choices may be set only for selection-type custom fields."
            })

        # A selection field's default (if any) must be present in its available choices
        if self.type == CustomFieldTypeChoices.TYPE_SELECT and self.default and self.default not in self.choices:
            raise ValidationError({
                'default': f"The specified default value ({self.default}) is not listed as an available choice."
            })

    def to_form_field(self, set_initial=True, enforce_required=True, for_csv_import=False):
        """
        Return a form field suitable for setting a CustomField's value for an object.

        set_initial: Set initial date for the field. This should be False when generating a field for bulk editing.
        enforce_required: Honor the value of CustomField.required. Set to False for filtering/bulk editing.
        for_csv_import: Return a form field suitable for bulk import of objects in CSV format.
        """
        initial = self.default if set_initial else None
        required = self.required if enforce_required else False

        # Integer
        if self.type == CustomFieldTypeChoices.TYPE_INTEGER:
            field = forms.IntegerField(
                required=required,
                initial=initial,
                min_value=self.validation_minimum,
                max_value=self.validation_maximum
            )

        # Boolean
        elif self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            choices = (
                (None, '---------'),
                (True, 'True'),
                (False, 'False'),
            )
            if initial is not None:
                initial = bool(initial)
            field = forms.NullBooleanField(
                required=required, initial=initial, widget=StaticSelect2(choices=choices)
            )

        # Date
        elif self.type == CustomFieldTypeChoices.TYPE_DATE:
            field = forms.DateField(required=required, initial=initial, widget=DatePicker())

        # Select
        elif self.type == CustomFieldTypeChoices.TYPE_SELECT:
            choices = [(c, c) for c in self.choices]
            default_choice = self.default if self.default in self.choices else None

            if not required or default_choice is None:
                choices = add_blank_choice(choices)

            # Set the initial value to the first available choice (if any)
            if set_initial and default_choice:
                initial = default_choice

            field_class = CSVChoiceField if for_csv_import else forms.ChoiceField
            field = field_class(
                choices=choices, required=required, initial=initial, widget=StaticSelect2()
            )

        # URL
        elif self.type == CustomFieldTypeChoices.TYPE_URL:
            field = LaxURLField(required=required, initial=initial)

        # Text
        else:
            field = forms.CharField(max_length=255, required=required, initial=initial)
            if self.validation_regex:
                field.validators = [
                    RegexValidator(
                        regex=self.validation_regex,
                        message=mark_safe(f"Values must match this regex: <code>{self.validation_regex}</code>")
                    )
                ]

        field.model = self
        field.label = str(self)
        if self.description:
            field.help_text = self.description

        return field
