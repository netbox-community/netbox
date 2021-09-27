from django import forms
from django.utils.translation import gettext as _

from extras.forms import CustomFieldModelFilterForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import BootstrapMixin, DynamicModelMultipleChoiceField, TagFilterField


class TenantGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = TenantGroup
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_('Parent group'),
        fetch_trigger='open'
    )


class TenantFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Tenant
    field_groups = (
        ('q', 'tag'),
        ('group_id',),
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)
