import decimal
import json
import re
from datetime import datetime, date

import django_filters
from django import forms
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from extras.choices import *
from extras.data import CHOICE_SETS
from netbox.models import ChangeLoggedModel
from netbox.models.features import CloningMixin, ExportTemplatesMixin
from netbox.search import FieldTypes
from utilities import filters
from utilities.datetime import datetime_from_timestamp
from utilities.forms.fields import (
    CSVChoiceField, CSVModelChoiceField, CSVModelMultipleChoiceField, CSVMultipleChoiceField, DynamicChoiceField,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, DynamicMultipleChoiceField, JSONField, LaxURLField,
)
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets import APISelect, APISelectMultiple, DatePicker, DateTimePicker
from utilities.querysets import RestrictedQuerySet
from utilities.templatetags.builtins.filters import render_markdown
from utilities.validators import validate_regex

__all__ = (
    'CustomField',
    'CustomFieldChoiceSet',
    'CustomFieldManager',
)

SEARCH_TYPES = {
    CustomFieldTypeChoices.TYPE_TEXT: FieldTypes.STRING,
    CustomFieldTypeChoices.TYPE_LONGTEXT: FieldTypes.STRING,
    CustomFieldTypeChoices.TYPE_INTEGER: FieldTypes.INTEGER,
    CustomFieldTypeChoices.TYPE_DECIMAL: FieldTypes.FLOAT,
    CustomFieldTypeChoices.TYPE_DATE: FieldTypes.STRING,
    CustomFieldTypeChoices.TYPE_URL: FieldTypes.STRING,
}


class CustomFieldManager(models.Manager.from_queryset(RestrictedQuerySet)):
    use_in_migrations = True

    def get_for_model(self, model):
        """
        Return all CustomFields assigned to the given model.
        """
        content_type = ObjectType.objects.get_for_model(model._meta.concrete_model)
        return self.get_queryset().filter(object_types=content_type)

    def get_defaults_for_model(self, model):
        """
        Return a dictionary of serialized default values for all CustomFields applicable to the given model.
        """
        custom_fields = self.get_for_model(model).filter(default__isnull=False)
        return {
            cf.name: cf.default for cf in custom_fields
        }


class CustomField(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    object_types = models.ManyToManyField(
        to='core.ObjectType',
        related_name='custom_fields',
        help_text=_('The object(s) to which this field applies.')
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CustomFieldTypeChoices,
        default=CustomFieldTypeChoices.TYPE_TEXT,
        help_text=_('The type of data this custom field holds')
    )
    related_object_type = models.ForeignKey(
        to='core.ObjectType',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_('The type of NetBox object this field maps to (for object fields)')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        unique=True,
        help_text=_('Internal field name'),
        validators=(
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message=_("Only alphanumeric characters and underscores are allowed."),
                flags=re.IGNORECASE
            ),
            RegexValidator(
                regex=r'__',
                message=_("Double underscores are not permitted in custom field names."),
                flags=re.IGNORECASE,
                inverse_match=True
            ),
        )
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=50,
        blank=True,
        help_text=_(
            "Name of the field as displayed to users (if not provided, 'the field's name will be used)"
        )
    )
    group_name = models.CharField(
        verbose_name=_('group name'),
        max_length=50,
        blank=True,
        help_text=_("Custom fields within the same group will be displayed together")
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    required = models.BooleanField(
        verbose_name=_('required'),
        default=False,
        help_text=_("This field is required when creating new objects or editing an existing object.")
    )
    unique = models.BooleanField(
        verbose_name=_('must be unique'),
        default=False,
        help_text=_("The value of this field must be unique for the assigned object")
    )
    search_weight = models.PositiveSmallIntegerField(
        verbose_name=_('search weight'),
        default=1000,
        help_text=_(
            "Weighting for search. Lower values are considered more important. Fields with a search weight of zero "
            "will be ignored."
        )
    )
    filter_logic = models.CharField(
        verbose_name=_('filter logic'),
        max_length=50,
        choices=CustomFieldFilterLogicChoices,
        default=CustomFieldFilterLogicChoices.FILTER_LOOSE,
        help_text=_("Loose matches any instance of a given string; exact matches the entire field.")
    )
    default = models.JSONField(
        verbose_name=_('default'),
        blank=True,
        null=True,
        help_text=_(
            'Default value for the field (must be a JSON value). Encapsulate strings with double quotes (e.g. "Foo").'
        )
    )
    related_object_filter = models.JSONField(
        blank=True,
        null=True,
        help_text=_(
            'Filter the object selection choices using a query_params dict (must be a JSON value).'
            'Encapsulate strings with double quotes (e.g. "Foo").'
        )
    )
    weight = models.PositiveSmallIntegerField(
        default=100,
        verbose_name=_('display weight'),
        help_text=_('Fields with higher weights appear lower in a form.')
    )
    validation_minimum = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name=_('minimum value'),
        help_text=_('Minimum allowed value (for numeric fields)')
    )
    validation_maximum = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name=_('maximum value'),
        help_text=_('Maximum allowed value (for numeric fields)')
    )
    validation_regex = models.CharField(
        blank=True,
        validators=[validate_regex],
        max_length=500,
        verbose_name=_('validation regex'),
        help_text=_(
            'Regular expression to enforce on text field values. Use ^ and $ to force matching of entire string. For '
            'example, <code>^[A-Z]{3}$</code> will limit values to exactly three uppercase letters.'
        )
    )
    choice_set = models.ForeignKey(
        to='CustomFieldChoiceSet',
        on_delete=models.PROTECT,
        related_name='choices_for',
        verbose_name=_('choice set'),
        blank=True,
        null=True
    )
    ui_visible = models.CharField(
        max_length=50,
        choices=CustomFieldUIVisibleChoices,
        default=CustomFieldUIVisibleChoices.ALWAYS,
        verbose_name=_('UI visible'),
        help_text=_('Specifies whether the custom field is displayed in the UI')
    )
    ui_editable = models.CharField(
        max_length=50,
        choices=CustomFieldUIEditableChoices,
        default=CustomFieldUIEditableChoices.YES,
        verbose_name=_('UI editable'),
        help_text=_('Specifies whether the custom field value can be edited in the UI')
    )
    is_cloneable = models.BooleanField(
        default=False,
        verbose_name=_('is cloneable'),
        help_text=_('Replicate this value when cloning objects')
    )
    comments = models.TextField(
        verbose_name=_('comments'),
        blank=True
    )

    objects = CustomFieldManager()

    clone_fields = (
        'object_types', 'type', 'related_object_type', 'group_name', 'description', 'required', 'unique',
        'search_weight', 'filter_logic', 'default', 'weight', 'validation_minimum', 'validation_maximum',
        'validation_regex', 'choice_set', 'ui_visible', 'ui_editable', 'is_cloneable',
    )

    class Meta:
        ordering = ['group_name', 'weight', 'name']
        verbose_name = _('custom field')
        verbose_name_plural = _('custom fields')

    def __str__(self):
        return self.label or self.name.replace('_', ' ').capitalize()

    def get_absolute_url(self):
        return reverse('extras:customfield', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/customfield/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache instance's original name so we can check later whether it has changed
        self._name = self.__dict__.get('name')

    @property
    def search_type(self):
        return SEARCH_TYPES.get(self.type)

    @property
    def choices(self):
        if self.choice_set:
            return self.choice_set.choices
        return []

    def get_ui_visible_color(self):
        return CustomFieldUIVisibleChoices.colors.get(self.ui_visible)

    def get_ui_editable_color(self):
        return CustomFieldUIEditableChoices.colors.get(self.ui_editable)

    def get_choice_label(self, value):
        if not hasattr(self, '_choice_map'):
            self._choice_map = dict(self.choices)
        return self._choice_map.get(value, value)

    def populate_initial_data(self, content_types):
        """
        Populate initial custom field data upon either a) the creation of a new CustomField, or
        b) the assignment of an existing CustomField to new object types.
        """
        for ct in content_types:
            model = ct.model_class()
            instances = model.objects.exclude(**{'custom_field_data__contains': self.name})
            for instance in instances:
                instance.custom_field_data[self.name] = self.default
            model.objects.bulk_update(instances, ['custom_field_data'], batch_size=100)

    def remove_stale_data(self, content_types):
        """
        Delete custom field data which is no longer relevant (either because the CustomField is
        no longer assigned to a model, or because it has been deleted).
        """
        for ct in content_types:
            if model := ct.model_class():
                instances = model.objects.filter(custom_field_data__has_key=self.name)
                for instance in instances:
                    del instance.custom_field_data[self.name]
                model.objects.bulk_update(instances, ['custom_field_data'], batch_size=100)

    def rename_object_data(self, old_name, new_name):
        """
        Called when a CustomField has been renamed. Updates all assigned object data.
        """
        for ct in self.object_types.all():
            model = ct.model_class()
            params = {f'custom_field_data__{old_name}__isnull': False}
            instances = model.objects.filter(**params)
            for instance in instances:
                instance.custom_field_data[new_name] = instance.custom_field_data.pop(old_name)
            model.objects.bulk_update(instances, ['custom_field_data'], batch_size=100)

    def clean(self):
        super().clean()

        # Validate the field's default value (if any)
        if self.default is not None:
            try:
                if self.type in (CustomFieldTypeChoices.TYPE_TEXT, CustomFieldTypeChoices.TYPE_LONGTEXT):
                    default_value = str(self.default)
                else:
                    default_value = self.default
                self.validate(default_value)
            except ValidationError as err:
                raise ValidationError({
                    'default': _(
                        'Invalid default value "{value}": {error}'
                    ).format(value=self.default, error=err.message)
                })

        # Minimum/maximum values can be set only for numeric fields
        if self.type not in (CustomFieldTypeChoices.TYPE_INTEGER, CustomFieldTypeChoices.TYPE_DECIMAL):
            if self.validation_minimum:
                raise ValidationError({'validation_minimum': _("A minimum value may be set only for numeric fields")})
            if self.validation_maximum:
                raise ValidationError({'validation_maximum': _("A maximum value may be set only for numeric fields")})

        # Regex validation can be set only for text fields
        regex_types = (
            CustomFieldTypeChoices.TYPE_TEXT,
            CustomFieldTypeChoices.TYPE_LONGTEXT,
            CustomFieldTypeChoices.TYPE_URL,
        )
        if self.validation_regex and self.type not in regex_types:
            raise ValidationError({
                'validation_regex': _("Regular expression validation is supported only for text and URL fields")
            })

        # Uniqueness can not be enforced for boolean fields
        if self.unique and self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            raise ValidationError({
                'unique': _("Uniqueness cannot be enforced for boolean fields")
            })

        # Choice set must be set on selection fields, and *only* on selection fields
        if self.type in (
                CustomFieldTypeChoices.TYPE_SELECT,
                CustomFieldTypeChoices.TYPE_MULTISELECT
        ):
            if not self.choice_set:
                raise ValidationError({
                    'choice_set': _("Selection fields must specify a set of choices.")
                })
        elif self.choice_set:
            raise ValidationError({
                'choice_set': _("Choices may be set only on selection fields.")
            })

        # Object fields must define an object_type; other fields must not
        if self.type in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT):
            if not self.related_object_type:
                raise ValidationError({
                    'related_object_type': _("Object fields must define an object type.")
                })
        elif self.related_object_type:
            raise ValidationError({
                'type': _("{type} fields may not define an object type.") .format(type=self.get_type_display())
            })

        # Related object filter can be set only for object-type fields, and must contain a dictionary mapping (if set)
        if self.related_object_filter is not None:
            if self.type not in (CustomFieldTypeChoices.TYPE_OBJECT, CustomFieldTypeChoices.TYPE_MULTIOBJECT):
                raise ValidationError({
                    'related_object_filter': _("A related object filter can be defined only for object fields.")
                })
            if type(self.related_object_filter) is not dict:
                raise ValidationError({
                    'related_object_filter': _("Filter must be defined as a dictionary mapping attributes to values.")
                })

    def serialize(self, value):
        """
        Prepare a value for storage as JSON data.
        """
        if value is None:
            return value
        if self.type == CustomFieldTypeChoices.TYPE_DATE and type(value) is date:
            return value.isoformat()
        if self.type == CustomFieldTypeChoices.TYPE_DATETIME and type(value) is datetime:
            return value.isoformat()
        if self.type == CustomFieldTypeChoices.TYPE_OBJECT:
            return value.pk
        if self.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            return [obj.pk for obj in value] or None
        return value

    def deserialize(self, value):
        """
        Convert JSON data to a Python object suitable for the field type.
        """
        if value is None:
            return value
        if self.type == CustomFieldTypeChoices.TYPE_DATE:
            try:
                return date.fromisoformat(value)
            except ValueError:
                return value
        if self.type == CustomFieldTypeChoices.TYPE_DATETIME:
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value
        if self.type == CustomFieldTypeChoices.TYPE_OBJECT:
            model = self.related_object_type.model_class()
            return model.objects.filter(pk=value).first()
        if self.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            model = self.related_object_type.model_class()
            return model.objects.filter(pk__in=value)
        return value

    def to_form_field(self, set_initial=True, enforce_required=True, enforce_visibility=True, for_csv_import=False):
        """
        Return a form field suitable for setting a CustomField's value for an object.

        set_initial: Set initial data for the field. This should be False when generating a field for bulk editing.
        enforce_required: Honor the value of CustomField.required. Set to False for filtering/bulk editing.
        enforce_visibility: Honor the value of CustomField.ui_visible. Set to False for filtering.
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

        # Decimal
        elif self.type == CustomFieldTypeChoices.TYPE_DECIMAL:
            field = forms.DecimalField(
                required=required,
                initial=initial,
                max_digits=12,
                decimal_places=4,
                min_value=self.validation_minimum,
                max_value=self.validation_maximum
            )

        # Boolean
        elif self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            choices = (
                (None, '---------'),
                (True, _('True')),
                (False, _('False')),
            )
            field = forms.NullBooleanField(
                required=required, initial=initial, widget=forms.Select(choices=choices)
            )

        # Date
        elif self.type == CustomFieldTypeChoices.TYPE_DATE:
            field = forms.DateField(required=required, initial=initial, widget=DatePicker())

        # Date & time
        elif self.type == CustomFieldTypeChoices.TYPE_DATETIME:
            field = forms.DateTimeField(required=required, initial=initial, widget=DateTimePicker())

        # Select
        elif self.type in (CustomFieldTypeChoices.TYPE_SELECT, CustomFieldTypeChoices.TYPE_MULTISELECT):
            choices = self.choice_set.choices
            default_choice = self.default if self.default in self.choices else None

            if not required or default_choice is None:
                choices = add_blank_choice(choices)

            # Set the initial value to the first available choice (if any)
            if set_initial and default_choice:
                initial = default_choice

            if for_csv_import:
                if self.type == CustomFieldTypeChoices.TYPE_SELECT:
                    field_class = CSVChoiceField
                else:
                    field_class = CSVMultipleChoiceField
                field = field_class(choices=choices, required=required, initial=initial)
            else:
                if self.type == CustomFieldTypeChoices.TYPE_SELECT:
                    field_class = DynamicChoiceField
                    widget_class = APISelect
                else:
                    field_class = DynamicMultipleChoiceField
                    widget_class = APISelectMultiple
                field = field_class(
                    choices=choices,
                    required=required,
                    initial=initial,
                    widget=widget_class(api_url=f'/api/extras/custom-field-choice-sets/{self.choice_set.pk}/choices/')
                )

        # URL
        elif self.type == CustomFieldTypeChoices.TYPE_URL:
            field = LaxURLField(required=required, initial=initial)

        # JSON
        elif self.type == CustomFieldTypeChoices.TYPE_JSON:
            field = JSONField(required=required, initial=json.dumps(initial) if initial else None)

        # Object
        elif self.type == CustomFieldTypeChoices.TYPE_OBJECT:
            model = self.related_object_type.model_class()
            field_class = CSVModelChoiceField if for_csv_import else DynamicModelChoiceField
            kwargs = {
                'queryset': model.objects.all(),
                'required': required,
                'initial': initial,
            }
            if not for_csv_import:
                kwargs['query_params'] = self.related_object_filter

            field = field_class(**kwargs)

        # Multiple objects
        elif self.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            model = self.related_object_type.model_class()
            field_class = CSVModelMultipleChoiceField if for_csv_import else DynamicModelMultipleChoiceField
            kwargs = {
                'queryset': model.objects.all(),
                'required': required,
                'initial': initial,
            }
            if not for_csv_import:
                kwargs['query_params'] = self.related_object_filter

            field = field_class(**kwargs)

        # Text
        else:
            widget = forms.Textarea if self.type == CustomFieldTypeChoices.TYPE_LONGTEXT else None
            field = forms.CharField(required=required, initial=initial, widget=widget)
            if self.validation_regex:
                field.validators = [
                    RegexValidator(
                        regex=self.validation_regex,
                        message=mark_safe(_("Values must match this regex: <code>{regex}</code>").format(
                            regex=escape(self.validation_regex)
                        ))
                    )
                ]

        field.model = self
        field.label = str(self)
        if self.description:
            field.help_text = render_markdown(self.description)

        # Annotate read-only fields
        if enforce_visibility and self.ui_editable != CustomFieldUIEditableChoices.YES:
            field.disabled = True

        return field

    def to_filter(self, lookup_expr=None):
        """
        Return a django_filters Filter instance suitable for this field type.

        :param lookup_expr: Custom lookup expression (optional)
        """
        kwargs = {
            'field_name': f'custom_field_data__{self.name}'
        }
        if lookup_expr is not None:
            kwargs['lookup_expr'] = lookup_expr

        # Text/URL
        if self.type in (
                CustomFieldTypeChoices.TYPE_TEXT,
                CustomFieldTypeChoices.TYPE_LONGTEXT,
                CustomFieldTypeChoices.TYPE_URL,
        ):
            filter_class = filters.MultiValueCharFilter
            if self.filter_logic == CustomFieldFilterLogicChoices.FILTER_LOOSE:
                kwargs['lookup_expr'] = 'icontains'

        # Integer
        elif self.type == CustomFieldTypeChoices.TYPE_INTEGER:
            filter_class = filters.MultiValueNumberFilter

        # Decimal
        elif self.type == CustomFieldTypeChoices.TYPE_DECIMAL:
            filter_class = filters.MultiValueDecimalFilter

        # Boolean
        elif self.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
            filter_class = django_filters.BooleanFilter

        # Date
        elif self.type == CustomFieldTypeChoices.TYPE_DATE:
            filter_class = filters.MultiValueDateFilter

        # Date & time
        elif self.type == CustomFieldTypeChoices.TYPE_DATETIME:
            filter_class = filters.MultiValueDateTimeFilter

        # Select
        elif self.type == CustomFieldTypeChoices.TYPE_SELECT:
            filter_class = filters.MultiValueCharFilter

        # Multiselect
        elif self.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
            filter_class = filters.MultiValueArrayFilter

        # Object
        elif self.type == CustomFieldTypeChoices.TYPE_OBJECT:
            filter_class = filters.MultiValueNumberFilter

        # Multi-object
        elif self.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            filter_class = filters.MultiValueNumberFilter
            kwargs['lookup_expr'] = 'contains'

        # Unsupported custom field type
        else:
            return None

        filter_instance = filter_class(**kwargs)
        filter_instance.custom_field = self

        return filter_instance

    def validate(self, value):
        """
        Validate a value according to the field's type validation rules.
        """
        if value not in [None, '']:

            # Validate text field
            if self.type in (CustomFieldTypeChoices.TYPE_TEXT, CustomFieldTypeChoices.TYPE_LONGTEXT):
                if type(value) is not str:
                    raise ValidationError(_("Value must be a string."))
                if self.validation_regex and not re.match(self.validation_regex, value):
                    raise ValidationError(_("Value must match regex '{regex}'").format(regex=self.validation_regex))

            # Validate integer
            elif self.type == CustomFieldTypeChoices.TYPE_INTEGER:
                if type(value) is not int:
                    raise ValidationError(_("Value must be an integer."))
                if self.validation_minimum is not None and value < self.validation_minimum:
                    raise ValidationError(
                        _("Value must be at least {minimum}").format(minimum=self.validation_minimum)
                    )
                if self.validation_maximum is not None and value > self.validation_maximum:
                    raise ValidationError(
                        _("Value must not exceed {maximum}").format(maximum=self.validation_maximum)
                    )

            # Validate decimal
            elif self.type == CustomFieldTypeChoices.TYPE_DECIMAL:
                try:
                    decimal.Decimal(value)
                except decimal.InvalidOperation:
                    raise ValidationError(_("Value must be a decimal."))
                if self.validation_minimum is not None and value < self.validation_minimum:
                    raise ValidationError(
                        _("Value must be at least {minimum}").format(minimum=self.validation_minimum)
                    )
                if self.validation_maximum is not None and value > self.validation_maximum:
                    raise ValidationError(
                        _("Value must not exceed {maximum}").format(maximum=self.validation_maximum)
                    )

            # Validate boolean
            elif self.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value not in [True, False, 1, 0]:
                raise ValidationError(_("Value must be true or false."))

            # Validate date
            elif self.type == CustomFieldTypeChoices.TYPE_DATE:
                if type(value) is not date:
                    try:
                        date.fromisoformat(value)
                    except ValueError:
                        raise ValidationError(_("Date values must be in ISO 8601 format (YYYY-MM-DD)."))

            # Validate date & time
            elif self.type == CustomFieldTypeChoices.TYPE_DATETIME:
                if type(value) is not datetime:
                    try:
                        datetime_from_timestamp(value)
                    except ValueError:
                        raise ValidationError(
                            _("Date and time values must be in ISO 8601 format (YYYY-MM-DD HH:MM:SS).")
                        )

            # Validate selected choice
            elif self.type == CustomFieldTypeChoices.TYPE_SELECT:
                if value not in self.choice_set.values:
                    raise ValidationError(
                        _("Invalid choice ({value}) for choice set {choiceset}.").format(
                            value=value,
                            choiceset=self.choice_set
                        )
                    )

            # Validate all selected choices
            elif self.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
                if not set(value).issubset(self.choice_set.values):
                    raise ValidationError(
                        _("Invalid choice(s) ({value}) for choice set {choiceset}.").format(
                            value=value,
                            choiceset=self.choice_set
                        )
                    )

            # Validate selected object
            elif self.type == CustomFieldTypeChoices.TYPE_OBJECT:
                if type(value) is not int:
                    raise ValidationError(_("Value must be an object ID, not {type}").format(type=type(value).__name__))

            # Validate selected objects
            elif self.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
                if type(value) is not list:
                    raise ValidationError(
                        _("Value must be a list of object IDs, not {type}").format(type=type(value).__name__)
                    )
                for id in value:
                    if type(id) is not int:
                        raise ValidationError(_("Found invalid object ID: {id}").format(id=id))

        elif self.required:
            raise ValidationError(_("Required field cannot be empty."))


class CustomFieldChoiceSet(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    Represents a set of choices available for choice and multi-choice custom fields.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    base_choices = models.CharField(
        max_length=50,
        choices=CustomFieldChoiceSetBaseChoices,
        blank=True,
        null=True,
        help_text=_('Base set of predefined choices (optional)')
    )
    extra_choices = ArrayField(
        ArrayField(
            base_field=models.CharField(max_length=100),
            size=2
        ),
        blank=True,
        null=True
    )
    order_alphabetically = models.BooleanField(
        default=False,
        help_text=_('Choices are automatically ordered alphabetically')
    )

    clone_fields = ('extra_choices', 'order_alphabetically')

    class Meta:
        ordering = ('name',)
        verbose_name = _('custom field choice set')
        verbose_name_plural = _('custom field choice sets')

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the initial set of choices for comparison under clean()
        self._original_extra_choices = self.__dict__.get('extra_choices')

    def get_absolute_url(self):
        return reverse('extras:customfieldchoiceset', args=[self.pk])

    @property
    def choices(self):
        """
        Returns a concatenation of the base and extra choices.
        """
        if not hasattr(self, '_choices'):
            self._choices = []
            if self.base_choices:
                self._choices.extend(CHOICE_SETS.get(self.base_choices))
            if self.extra_choices:
                self._choices.extend(self.extra_choices)
        if self.order_alphabetically:
            self._choices = sorted(self._choices, key=lambda x: x[0])
        return self._choices

    @property
    def choices_count(self):
        return len(self.choices)

    @property
    def values(self):
        """
        Returns an iterator of the valid choice values.
        """
        return (x[0] for x in self.choices)

    def clean(self):
        if not self.base_choices and not self.extra_choices:
            raise ValidationError(_("Must define base or extra choices."))

        # Check whether any choices have been removed. If so, check whether any of the removed
        # choices are still set in custom field data for any object.
        original_choices = set([
            c[0] for c in self._original_extra_choices
        ]) if self._original_extra_choices else set()
        current_choices = set([
            c[0] for c in self.extra_choices
        ]) if self.extra_choices else set()
        if removed_choices := original_choices - current_choices:
            for custom_field in self.choices_for.all():
                for object_type in custom_field.object_types.all():
                    model = object_type.model_class()
                    for choice in removed_choices:
                        # Form the query based on the type of custom field
                        if custom_field.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
                            query_args = {f"custom_field_data__{custom_field.name}__contains": choice}
                        else:
                            query_args = {f"custom_field_data__{custom_field.name}": choice}
                        # Raise a ValidationError if there are any objects which still reference the removed choice
                        if model.objects.filter(models.Q(**query_args)).exists():
                            raise ValidationError(
                                _(
                                    "Cannot remove choice {choice} as there are {model} objects which reference it."
                                ).format(choice=choice, model=object_type)
                            )

    def save(self, *args, **kwargs):

        # Sort choices if alphabetical ordering is enforced
        if self.order_alphabetically:
            self.extra_choices = sorted(self.extra_choices, key=lambda x: x[0])

        return super().save(*args, **kwargs)
