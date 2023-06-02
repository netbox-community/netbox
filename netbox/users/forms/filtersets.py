from django import forms
from django.utils.translation import gettext as _

from circuits.choices import CircuitCommitRateChoices, CircuitStatusChoices
from circuits.models import *
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import TenancyFilterForm, ContactModelFilterForm
from users.models import NetBoxUser
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import DatePicker, NumberWithOptions

__all__ = (
    'UserFilterForm',
)


class UserFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = NetBoxUser
    fieldsets = (
        (None, ('q', 'filter_id',)),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('ASN', ('asn',)),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    asn = forms.IntegerField(
        required=False,
        label=_('ASN (legacy)')
    )
    asn_id = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        required=False,
        label=_('ASNs')
    )
    tag = TagFilterField(model)
