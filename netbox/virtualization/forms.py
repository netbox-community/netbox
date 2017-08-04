from __future__ import unicode_literals

from django import forms

from extras.forms import CustomFieldBulkEditForm, CustomFieldForm
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import BootstrapMixin, SlugField
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine


#
# Cluster types
#

class ClusterTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ['name', 'slug']


#
# Cluster groups
#

class ClusterGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ['name', 'slug']


#
# Clusters
#

class ClusterForm(BootstrapMixin, CustomFieldForm):

    class Meta:
        model = Cluster
        fields = ['name', 'type', 'group']


class ClusterCSVForm(forms.ModelForm):
    type = forms.ModelChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text='Name of cluster type',
        error_messages={
            'invalid_choice': 'Invalid cluster type name.',
        }
    )
    group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of cluster group',
        error_messages={
            'invalid_choice': 'Invalid cluster group name.',
        }
    )

    class Meta:
        fields = ['name', 'type', 'group']


#
# Virtual Machines
#

class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldForm):

    class Meta:
        model = VirtualMachine
        fields = ['name', 'cluster', 'tenant', 'platform', 'comments']


class VirtualMachineCSVForm(forms.ModelForm):
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        help_text='Name of parent cluster',
        error_messages={
            'invalid_choice': 'Invalid cluster name.',
        }
    )

    class Meta:
        fields = ['cluster', 'name', 'tenant']


class VirtualMachineBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), widget=forms.MultipleHiddenInput)
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all(), required=False, label='Cluster')
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        nullable_fields = ['tenant']
