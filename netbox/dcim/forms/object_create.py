from django import forms

from dcim.models import *
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField, ExpandableNameField,
)

__all__ = (
    'ComponentCreateForm',
    'VirtualChassisCreateForm',
)


class ComponentCreateForm(BootstrapMixin, forms.Form):
    """
    Subclass this form when facilitating the creation of one or more device component or component templates based on
    a name pattern.
    """
    name_pattern = ExpandableNameField(
        label='Name'
    )
    label_pattern = ExpandableNameField(
        label='Label',
        required=False,
        help_text='Alphanumeric ranges are supported. (Must match the number of names being created.)'
    )

    def clean(self):
        super().clean()

        # Validate that the number of components being created from both the name_pattern and label_pattern are equal
        if self.cleaned_data['label_pattern']:
            name_pattern_count = len(self.cleaned_data['name_pattern'])
            label_pattern_count = len(self.cleaned_data['label_pattern'])
            if name_pattern_count != label_pattern_count:
                raise forms.ValidationError({
                    'label_pattern': f'The provided name pattern will create {name_pattern_count} components, however '
                                     f'{label_pattern_count} labels will be generated. These counts must match.'
                }, code='label_pattern_mismatch')


class VirtualChassisCreateForm(CustomFieldModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    members = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
        }
    )
    initial_position = forms.IntegerField(
        initial=1,
        required=False,
        help_text='Position of the first member device. Increases by one for each additional member.'
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'region', 'site_group', 'site', 'rack', 'members', 'initial_position', 'tags',
        ]

    def clean(self):
        if self.cleaned_data['members'] and self.cleaned_data['initial_position'] is None:
            raise forms.ValidationError({
                'initial_position': "A position must be specified for the first VC member."
            })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Assign VC members
        if instance.pk and self.cleaned_data['members']:
            initial_position = self.cleaned_data.get('initial_position', 1)
            for i, member in enumerate(self.cleaned_data['members'], start=initial_position):
                member.virtual_chassis = instance
                member.vc_position = i
                member.save()

        return instance
