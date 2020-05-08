import logging
from collections import OrderedDict
from datetime import date

from django import forms
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.db import models

from utilities.forms import CSVChoiceField, DatePicker, LaxURLField, StaticSelect2, add_blank_choice
from extras.choices import *
from extras.utils import FeatureQuery


#
# Custom fields
#

class CustomFieldModel(models.Model):
    _cf = None

    class Meta:
        abstract = True

    def cache_custom_fields(self):
        """
        Cache all custom field values for this instance
        """
        self._cf = {
            field.name: value for field, value in self.get_custom_fields().items()
        }

    @property
    def cf(self):
        """
        Name-based CustomFieldValue accessor for use in templates
        """
        if self._cf is None:
            self.cache_custom_fields()
        return self._cf

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form {<field>: value}.
        """
        fields = CustomField.objects.get_for_model(self)

        # If the object exists, populate its custom fields with values
        if hasattr(self, 'pk'):
            values = self.custom_field_values.all()
            values_dict = {cfv.field_id: cfv.value for cfv in values}
            return OrderedDict([(field, values_dict.get(field.pk)) for field in fields])
        else:
            return OrderedDict([(field, None) for field in fields])


class CustomFieldManager(models.Manager):
    use_in_migrations = True

    def get_for_model(self, model):
        """
        Return all CustomFields assigned to the given model.
        """
        model = model._meta.concrete_model

        # Fetch from the database if the model's CustomFields have not been cached
        content_type = ContentType.objects.get_for_model(model)
        customfields = CustomField.objects.filter(obj_type=content_type)

        return customfields


class CustomField(models.Model):
    obj_type = models.ManyToManyField(
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
        unique=True
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

    objects = CustomFieldManager()

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.label or self.name.replace('_', ' ').capitalize()

    def serialize_value(self, value):
        """
        Serialize the given value to a string suitable for storage as a CustomFieldValue
        """
        if value is None:
            return ''
        if self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            return str(int(bool(value)))
        if self.type == CustomFieldTypeChoices.TYPE_DATE:
            # Could be date/datetime object or string
            try:
                return value.strftime('%Y-%m-%d')
            except AttributeError:
                return value
        if self.type == CustomFieldTypeChoices.TYPE_SELECT:
            # Could be ModelChoiceField or TypedChoiceField
            return str(value.id) if hasattr(value, 'id') else str(value)
        return value

    def deserialize_value(self, serialized_value):
        """
        Convert a string into the object it represents depending on the type of field
        """
        if serialized_value == '':
            return None
        if self.type == CustomFieldTypeChoices.TYPE_INTEGER:
            return int(serialized_value)
        if self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            return bool(int(serialized_value))
        if self.type == CustomFieldTypeChoices.TYPE_DATE:
            # Read date as YYYY-MM-DD
            return date(*[int(n) for n in serialized_value.split('-')])
        if self.type == CustomFieldTypeChoices.TYPE_SELECT:
            return self.choices.get(pk=int(serialized_value))
        return serialized_value

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
            field = forms.IntegerField(required=required, initial=initial)

        # Boolean
        elif self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            choices = (
                (None, '---------'),
                (1, 'True'),
                (0, 'False'),
            )
            if initial is not None and initial.lower() in ['true', 'yes', '1']:
                initial = 1
            elif initial is not None and initial.lower() in ['false', 'no', '0']:
                initial = 0
            else:
                initial = None
            field = forms.NullBooleanField(
                required=required, initial=initial, widget=StaticSelect2(choices=choices)
            )

        # Date
        elif self.type == CustomFieldTypeChoices.TYPE_DATE:
            field = forms.DateField(required=required, initial=initial, widget=DatePicker())

        # Select
        elif self.type == CustomFieldTypeChoices.TYPE_SELECT:
            choices = [(cfc.pk, cfc.value) for cfc in self.choices.all()]

            if not required:
                choices = add_blank_choice(choices)

            # Set the initial value to the PK of the default choice, if any
            if set_initial:
                default_choice = self.choices.filter(value=self.default).first()
                if default_choice:
                    initial = default_choice.pk

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

        field.model = self
        field.label = self.label if self.label else self.name.replace('_', ' ').capitalize()
        if self.description:
            field.help_text = self.description

        return field


class CustomFieldValue(models.Model):
    field = models.ForeignKey(
        to='extras.CustomField',
        on_delete=models.CASCADE,
        related_name='values'
    )
    obj_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        related_name='+'
    )
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey(
        ct_field='obj_type',
        fk_field='obj_id'
    )
    serialized_value = models.CharField(
        max_length=255
    )

    class Meta:
        ordering = ('obj_type', 'obj_id', 'pk')  # (obj_type, obj_id) may be non-unique
        unique_together = ('field', 'obj_type', 'obj_id')

    def __str__(self):
        return '{} {}'.format(self.obj, self.field)

    @property
    def value(self):
        return self.field.deserialize_value(self.serialized_value)

    @value.setter
    def value(self, value):
        self.serialized_value = self.field.serialize_value(value)

    def save(self, *args, **kwargs):
        # Delete this object if it no longer has a value to store
        if self.pk and self.value is None:
            self.delete()
        else:
            super().save(*args, **kwargs)


class CustomFieldChoice(models.Model):
    field = models.ForeignKey(
        to='extras.CustomField',
        on_delete=models.CASCADE,
        related_name='choices',
        limit_choices_to={'type': CustomFieldTypeChoices.TYPE_SELECT}
    )
    value = models.CharField(
        max_length=100
    )
    weight = models.PositiveSmallIntegerField(
        default=100,
        help_text='Higher weights appear lower in the list'
    )

    class Meta:
        ordering = ['field', 'weight', 'value']
        unique_together = ['field', 'value']

    def __str__(self):
        return self.value

    def clean(self):
        if self.field.type != CustomFieldTypeChoices.TYPE_SELECT:
            raise ValidationError("Custom field choices can only be assigned to selection fields.")

    def delete(self, using=None, keep_parents=False):
        # When deleting a CustomFieldChoice, delete all CustomFieldValues which point to it
        pk = self.pk
        super().delete(using, keep_parents)
        CustomFieldValue.objects.filter(
            field__type=CustomFieldTypeChoices.TYPE_SELECT,
            serialized_value=str(pk)
        ).delete()
