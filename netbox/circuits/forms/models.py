from django import forms

from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from tenancy.forms import TenancyForm
from utilities.forms import (
    BootstrapMixin, CommentField, DatePicker, DynamicModelChoiceField, DynamicModelMultipleChoiceField,
    SelectSpeedWidget, SmallTextarea, SlugField, StaticSelect,
)

__all__ = (
    'CircuitForm',
    'CircuitTerminationForm',
    'CircuitTypeForm',
    'ProviderForm',
    'ProviderNetworkForm',
)


class ProviderForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags',
        ]
        fieldsets = (
            ('Provider', ('name', 'slug', 'asn', 'tags')),
            ('Support Info', ('account', 'portal_url', 'noc_contact', 'admin_contact')),
        )
        widgets = {
            'noc_contact': SmallTextarea(
                attrs={'rows': 5}
            ),
            'admin_contact': SmallTextarea(
                attrs={'rows': 5}
            ),
        }
        help_texts = {
            'name': "Full name of the provider",
            'asn': "BGP autonomous system number (if applicable)",
            'portal_url': "URL of the provider's customer support portal",
            'noc_contact': "NOC email address and phone number",
            'admin_contact': "Administrative contact email address and phone number",
        }


class ProviderNetworkForm(BootstrapMixin, CustomFieldModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'description', 'comments', 'tags',
        ]
        fieldsets = (
            ('Provider Network', ('provider', 'name', 'description', 'tags')),
        )


class CircuitTypeForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class CircuitForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'status', 'install_date', 'commit_rate', 'description', 'tenant_group', 'tenant',
            'comments', 'tags',
        ]
        fieldsets = (
            ('Circuit', ('provider', 'cid', 'type', 'status', 'install_date', 'commit_rate', 'description', 'tags')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )
        help_texts = {
            'cid': "Unique circuit ID",
            'commit_rate': "Committed rate",
        }
        widgets = {
            'status': StaticSelect(),
            'install_date': DatePicker(),
            'commit_rate': SelectSpeedWidget(),
        }


class CircuitTerminationForm(BootstrapMixin, forms.ModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        },
        required=False
    )
    provider_network = DynamicModelChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'term_side', 'region', 'site_group', 'site', 'provider_network', 'mark_connected', 'port_speed',
            'upstream_speed', 'xconnect_id', 'pp_info', 'description',
        ]
        help_texts = {
            'port_speed': "Physical circuit speed",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }
        widgets = {
            'term_side': forms.HiddenInput(),
            'port_speed': SelectSpeedWidget(),
            'upstream_speed': SelectSpeedWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['provider_network'].widget.add_query_param('provider_id', self.instance.circuit.provider_id)
