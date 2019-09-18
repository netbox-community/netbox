from collections import OrderedDict

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from taggit.forms import TagField

from dcim.models import DeviceRole, Platform, Region, Site
from tenancy.models import Tenant, TenantGroup
from utilities.constants import COLOR_CHOICES
from utilities.forms import (
    add_blank_choice, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect, ColorSelect,
    CommentField, ContentTypeSelect, FilterChoiceField, LaxURLField, JSONField, SlugField, StaticSelect2,
    BOOLEAN_WITH_BLANK_CHOICES,
)
from .constants import (
    CF_FILTER_DISABLED, CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_INTEGER, CF_TYPE_SELECT, CF_TYPE_URL,
    OBJECTCHANGE_ACTION_CHOICES,
)
from .models import ConfigContext, CustomField, CustomFieldValue, ImageAttachment, ObjectChange, Tag


#
# Custom fields
#

def get_custom_fields_for_model(content_type, filterable_only=False, bulk_edit=False):
    """
    Retrieve all CustomFields applicable to the given ContentType
    """
    field_dict = OrderedDict()
    custom_fields = CustomField.objects.filter(obj_type=content_type)
    if filterable_only:
        custom_fields = custom_fields.exclude(filter_logic=CF_FILTER_DISABLED)

    for cf in custom_fields:
        field_name = 'cf_{}'.format(str(cf.name))
        initial = cf.default if not bulk_edit else None

        # Integer
        if cf.type == CF_TYPE_INTEGER:
            field = forms.IntegerField(required=cf.required, initial=initial)

        # Boolean
        elif cf.type == CF_TYPE_BOOLEAN:
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
                required=cf.required, initial=initial, widget=forms.Select(choices=choices)
            )

        # Date
        elif cf.type == CF_TYPE_DATE:
            field = forms.DateField(required=cf.required, initial=initial, help_text="Date format: YYYY-MM-DD")

        # Select
        elif cf.type == CF_TYPE_SELECT:
            choices = [(cfc.pk, cfc) for cfc in cf.choices.all()]
            if not cf.required or bulk_edit or filterable_only:
                choices = [(None, '---------')] + choices
            # Check for a default choice
            default_choice = None
            if initial:
                try:
                    default_choice = cf.choices.get(value=initial).pk
                except ObjectDoesNotExist:
                    pass
            field = forms.TypedChoiceField(choices=choices, coerce=int, required=cf.required, initial=default_choice)

        # URL
        elif cf.type == CF_TYPE_URL:
            field = LaxURLField(required=cf.required, initial=initial)

        # Text
        else:
            field = forms.CharField(max_length=255, required=cf.required, initial=initial)

        field.model = cf
        field.label = cf.label if cf.label else cf.name.replace('_', ' ').capitalize()
        if cf.description:
            field.help_text = cf.description

        field_dict[field_name] = field

    return field_dict


class CustomFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.custom_fields = []
        self.obj_type = ContentType.objects.get_for_model(self._meta.model)

        super().__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        custom_fields = []
        for name, field in get_custom_fields_for_model(self.obj_type).items():
            self.fields[name] = field
            custom_fields.append(name)
        self.custom_fields = custom_fields

        # If editing an existing object, initialize values for all custom fields
        if self.instance.pk:
            existing_values = CustomFieldValue.objects.filter(
                obj_type=self.obj_type,
                obj_id=self.instance.pk
            ).prefetch_related('field')
            for cfv in existing_values:
                self.initial['cf_{}'.format(str(cfv.field.name))] = cfv.serialized_value

    def _save_custom_fields(self):

        for field_name in self.custom_fields:
            try:
                cfv = CustomFieldValue.objects.prefetch_related('field').get(
                    field=self.fields[field_name].model,
                    obj_type=self.obj_type,
                    obj_id=self.instance.pk
                )
            except CustomFieldValue.DoesNotExist:
                # Skip this field if none exists already and its value is empty
                if self.cleaned_data[field_name] in [None, '']:
                    continue
                cfv = CustomFieldValue(
                    field=self.fields[field_name].model,
                    obj_type=self.obj_type,
                    obj_id=self.instance.pk
                )
            cfv.value = self.cleaned_data[field_name]
            cfv.save()

    def save(self, commit=True):
        obj = super().save(commit)

        # Handle custom fields the same way we do M2M fields
        if commit:
            self._save_custom_fields()
        else:
            self.save_custom_fields = self._save_custom_fields

        return obj


class CustomFieldBulkEditForm(BulkEditForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.custom_fields = []
        self.obj_type = ContentType.objects.get_for_model(self.model)

        # Add all applicable CustomFields to the form
        custom_fields = get_custom_fields_for_model(self.obj_type, bulk_edit=True).items()
        for name, field in custom_fields:
            # Annotate non-required custom fields as nullable
            if not field.required:
                self.nullable_fields.append(name)
            field.required = False
            self.fields[name] = field
            # Annotate this as a custom field
            self.custom_fields.append(name)


class CustomFieldFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(self.model)

        super().__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        custom_fields = get_custom_fields_for_model(self.obj_type, filterable_only=True).items()
        for name, field in custom_fields:
            field.required = False
            self.fields[name] = field


#
# Tags
#

class TagForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = Tag
        fields = [
            'name', 'slug', 'color', 'comments'
        ]


class AddRemoveTagsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add add/remove tags fields
        self.fields['add_tags'] = TagField(required=False)
        self.fields['remove_tags'] = TagField(required=False)


class TagFilterForm(BootstrapMixin, forms.Form):
    model = Tag
    q = forms.CharField(
        required=False,
        label='Search'
    )


class TagBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    color = forms.CharField(
        max_length=6,
        required=False,
        widget=ColorSelect()
    )

    class Meta:
        nullable_fields = []


#
# Config contexts
#

class ConfigContextForm(BootstrapMixin, forms.ModelForm):
    data = JSONField(
        label=''
    )

    class Meta:
        model = ConfigContext
        fields = [
            'name', 'weight', 'description', 'is_active', 'regions', 'sites', 'roles', 'platforms', 'tenant_groups',
            'tenants', 'data',
        ]
        widgets = {
            'regions': APISelectMultiple(
                api_url="/api/dcim/regions/"
            ),
            'sites': APISelectMultiple(
                api_url="/api/dcim/sites/"
            ),
            'roles': APISelectMultiple(
                api_url="/api/dcim/device-roles/"
            ),
            'platforms': APISelectMultiple(
                api_url="/api/dcim/platforms/"
            ),
            'tenant_groups': APISelectMultiple(
                api_url="/api/tenancy/tenant-groups/"
            ),
            'tenants': APISelectMultiple(
                api_url="/api/tenancy/tenants/"
            )
        }


class ConfigContextBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ConfigContext.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        required=False,
        min_value=0
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    description = forms.CharField(
        required=False,
        max_length=100
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class ConfigContextFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(
        required=False,
        label='Search'
    )
    region = FilterChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/regions/",
            value_field="slug",
        )
    )
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )
    role = FilterChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/device-roles/",
            value_field="slug",
        )
    )
    platform = FilterChoiceField(
        queryset=Platform.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/platforms/",
            value_field="slug",
        )
    )
    tenant_group = FilterChoiceField(
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenant-groups/",
            value_field="slug",
        )
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/tenancy/tenants/",
            value_field="slug",
        )
    )


#
# Filter form for local config context data
#

class LocalConfigContextFilterForm(forms.Form):
    local_context_data = forms.NullBooleanField(
        required=False,
        label='Has local config context data',
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


#
# Image attachments
#

class ImageAttachmentForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = ImageAttachment
        fields = [
            'name', 'image',
        ]


#
# Change logging
#

class ObjectChangeFilterForm(BootstrapMixin, forms.Form):
    model = ObjectChange
    q = forms.CharField(
        required=False,
        label='Search'
    )
    time_after = forms.DateTimeField(
        label='After',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'YYYY-MM-DD hh:mm:ss'}
        )
    )
    time_before = forms.DateTimeField(
        label='Before',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'YYYY-MM-DD hh:mm:ss'}
        )
    )
    action = forms.ChoiceField(
        choices=add_blank_choice(OBJECTCHANGE_ACTION_CHOICES),
        required=False
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by('username'),
        required=False
    )
    changed_object_type = forms.ModelChoiceField(
        queryset=ContentType.objects.order_by('model'),
        required=False,
        widget=ContentTypeSelect(),
        label='Object Type'
    )


#
# Scripts
#

class ScriptForm(BootstrapMixin, forms.Form):
    _commit = forms.BooleanField(
        required=False,
        initial=True,
        label="Commit changes",
        help_text="Commit changes to the database (uncheck for a dry-run)"
    )

    def __init__(self, vars, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Dynamically populate fields for variables
        for name, var in vars.items():
            self.fields[name] = var.as_field()

        # Move _commit to the end of the form
        self.fields.move_to_end('_commit', True)

    @property
    def requires_input(self):
        """
        A boolean indicating whether the form requires user input (ignore the _commit field).
        """
        return bool(len(self.fields) > 1)
